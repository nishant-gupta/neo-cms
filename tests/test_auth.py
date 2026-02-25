from __future__ import annotations

import json
import os
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import auth
from app.main import app


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class AuthRoleModelTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GOOGLE_OAUTH_CLIENT_ID"] = "test-client-id.apps.googleusercontent.com"
        os.environ["CMS_ROLE_BINDINGS"] = json.dumps(
            {
                "editor@example.com": ["editor"],
                "publisher@example.com": ["publisher"],
                "admin@example.com": ["admin", "publisher", "editor"],
            }
        )
        auth.get_auth_settings.cache_clear()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        auth.get_auth_settings.cache_clear()

    @staticmethod
    def _fake_verify(token: str, audience: str) -> dict[str, object]:
        payloads = {
            "editor-token": {"email": "editor@example.com", "email_verified": True},
            "publisher-token": {"email": "publisher@example.com", "email_verified": True},
            "admin-token": {"email": "admin@example.com", "email_verified": True},
        }
        if token not in payloads:
            raise auth._unauthorized("Invalid Google OAuth token.")
        return payloads[token]

    def test_missing_token_returns_401(self) -> None:
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_returns_401(self) -> None:
        with mock.patch("app.auth.verify_google_oauth_token", side_effect=self._fake_verify):
            response = self.client.get("/api/v1/auth/me", headers=bearer("bad-token"))

        self.assertEqual(response.status_code, 401)

    def test_editor_forbidden_on_admin_endpoint_returns_403(self) -> None:
        with mock.patch("app.auth.verify_google_oauth_token", side_effect=self._fake_verify):
            response = self.client.get("/api/v1/admin/ping", headers=bearer("editor-token"))

        self.assertEqual(response.status_code, 403)

    def test_admin_allowed_on_admin_endpoint_returns_200(self) -> None:
        with mock.patch("app.auth.verify_google_oauth_token", side_effect=self._fake_verify):
            response = self.client.get("/api/v1/admin/ping", headers=bearer("admin-token"))

        self.assertEqual(response.status_code, 200)

    def test_publisher_allowed_on_publisher_endpoint_returns_200(self) -> None:
        with mock.patch("app.auth.verify_google_oauth_token", side_effect=self._fake_verify):
            response = self.client.get(
                "/api/v1/publisher/ping",
                headers=bearer("publisher-token"),
            )

        self.assertEqual(response.status_code, 200)

    def test_me_endpoint_returns_roles(self) -> None:
        with mock.patch("app.auth.verify_google_oauth_token", side_effect=self._fake_verify):
            response = self.client.get("/api/v1/auth/me", headers=bearer("admin-token"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["email"], "admin@example.com")
        self.assertIn("admin", payload["roles"])


if __name__ == "__main__":
    unittest.main()
