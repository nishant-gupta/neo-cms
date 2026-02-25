from __future__ import annotations

from fastapi import Depends, FastAPI

from app.auth import AuthenticatedUser, require_roles

app = FastAPI(title="neo-cms API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/auth/me")
def auth_me(
    user: AuthenticatedUser = Depends(require_roles("editor", "publisher", "admin")),
) -> dict[str, object]:
    return {
        "email": user.email,
        "roles": list(user.roles),
    }


@app.get("/api/v1/admin/ping")
def admin_ping(
    user: AuthenticatedUser = Depends(require_roles("admin")),
) -> dict[str, str]:
    return {"message": f"admin access granted for {user.email}"}


@app.get("/api/v1/publisher/ping")
def publisher_ping(
    user: AuthenticatedUser = Depends(require_roles("publisher", "admin")),
) -> dict[str, str]:
    return {"message": f"publisher access granted for {user.email}"}
