from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

VALID_ROLES = {"editor", "publisher", "admin"}
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthSettings:
    google_oauth_client_id: str
    role_bindings: dict[str, set[str]]


@dataclass(frozen=True)
class AuthenticatedUser:
    email: str
    roles: tuple[str, ...]


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _forbidden(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _normalize_role_bindings(raw_bindings: str) -> dict[str, set[str]]:
    if not raw_bindings:
        return {}

    try:
        parsed = json.loads(raw_bindings)
    except json.JSONDecodeError as exc:
        raise RuntimeError("CMS_ROLE_BINDINGS must be valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise RuntimeError("CMS_ROLE_BINDINGS must be a JSON object.")

    normalized: dict[str, set[str]] = {}
    for principal, roles in parsed.items():
        principal_key = str(principal).strip().lower()
        if not principal_key:
            continue

        if isinstance(roles, str):
            role_items = [roles]
        elif isinstance(roles, list):
            role_items = roles
        else:
            raise RuntimeError(
                f"CMS_ROLE_BINDINGS entry '{principal}' must be a string or list of strings."
            )

        cleaned_roles = {str(role).strip().lower() for role in role_items if str(role).strip()}
        invalid_roles = cleaned_roles - VALID_ROLES
        if invalid_roles:
            raise RuntimeError(
                f"Unsupported role(s) for '{principal}': {sorted(invalid_roles)}. "
                f"Valid roles: {sorted(VALID_ROLES)}."
            )

        normalized[principal_key] = cleaned_roles

    return normalized


@lru_cache(maxsize=1)
def get_auth_settings() -> AuthSettings:
    return AuthSettings(
        google_oauth_client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip(),
        role_bindings=_normalize_role_bindings(os.getenv("CMS_ROLE_BINDINGS", "{}")),
    )


def verify_google_oauth_token(token: str, audience: str) -> dict[str, Any]:
    if not audience:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_OAUTH_CLIENT_ID is not configured.",
        )

    try:
        payload = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=audience,
        )
    except ValueError as exc:
        raise _unauthorized("Invalid Google OAuth token.") from exc

    email = str(payload.get("email", "")).strip().lower()
    if not email:
        raise _unauthorized("Google OAuth token is missing email.")

    if payload.get("email_verified") is False:
        raise _unauthorized("Google account email must be verified.")

    return payload


def _resolve_roles(email: str, role_bindings: dict[str, set[str]]) -> tuple[str, ...]:
    return tuple(sorted(role_bindings.get(email.lower(), set())))


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: AuthSettings = Depends(get_auth_settings),
) -> AuthenticatedUser:
    if credentials is None:
        raise _unauthorized("Missing bearer token.")
    if credentials.scheme.lower() != "bearer":
        raise _unauthorized("Unsupported authorization scheme.")

    payload = verify_google_oauth_token(credentials.credentials, settings.google_oauth_client_id)
    email = str(payload["email"]).strip().lower()
    roles = _resolve_roles(email, settings.role_bindings)

    return AuthenticatedUser(email=email, roles=roles)


def require_roles(*required_roles: str):
    required = {role.strip().lower() for role in required_roles if role.strip()}
    invalid = required - VALID_ROLES
    if invalid:
        raise RuntimeError(
            f"Invalid required roles: {sorted(invalid)}. Valid roles: {sorted(VALID_ROLES)}."
        )

    def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if not required.intersection(user.roles):
            raise _forbidden(
                "Insufficient role privileges. "
                f"Required any of: {sorted(required)}."
            )
        return user

    return dependency
