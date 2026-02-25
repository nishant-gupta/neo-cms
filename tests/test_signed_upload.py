from __future__ import annotations

import json
import os
import unittest
from datetime import timedelta
from unittest import mock

from fastapi.testclient import TestClient

from app import auth
from app.main import app


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class _FakeBlob:
    def __init__(self) -> None:
        self.call_kwargs: dict[str, object] = {}

    def generate_signed_url(self, **kwargs: object) -> str:
        self.call_kwargs = kwargs
        return "https://storage.googleapis.com/upload-signed-url"


class _FakeBucket:
    def __init__(self, blob: _FakeBlob) -> None:
        self.blob_instance = blob
        self.object_name = ""

    def blob(self, object_name: str) -> _FakeBlob:
        self.object_name = object_name
        return self.blob_instance


class _FakeStorageClient:
    def __init__(self) -> None:
        self.bucket_name = ""
        self.blob = _FakeBlob()
        self.bucket_instance = _FakeBucket(self.blob)

    def bucket(self, name: str) -> _FakeBucket:
        self.bucket_name = name
        return self.bucket_instance


class SignedUploadUrlTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GOOGLE_OAUTH_CLIENT_ID"] = "test-client-id.apps.googleusercontent.com"
        os.environ["CMS_ROLE_BINDINGS"] = json.dumps({"editor@example.com": ["editor"]})
        os.environ["CMS_ASSETS_BUCKET"] = "cms-dev-assets"
        auth.get_auth_settings.cache_clear()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        auth.get_auth_settings.cache_clear()

    @staticmethod
    def _fake_verify(token: str, audience: str) -> dict[str, object]:
        if token == "editor-token":
            return {"email": "editor@example.com", "email_verified": True}
        raise auth._unauthorized("Invalid Google OAuth token.")

    def test_endpoint_requires_authentication(self) -> None:
        response = self.client.post(
            "/api/v1/assets/signed-upload-url",
            json={"filename": "hero.png", "mimeType": "image/png"},
        )
        self.assertEqual(response.status_code, 401)

    def test_endpoint_rejects_unsupported_mime_type(self) -> None:
        with mock.patch("app.auth.verify_google_oauth_token", side_effect=self._fake_verify):
            response = self.client.post(
                "/api/v1/assets/signed-upload-url",
                headers=bearer("editor-token"),
                json={"filename": "hero.bmp", "mimeType": "image/bmp"},
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported mime type", response.text)

    def test_endpoint_returns_signed_upload_url(self) -> None:
        fake_storage_client = _FakeStorageClient()

        with mock.patch("app.auth.verify_google_oauth_token", side_effect=self._fake_verify):
            with mock.patch("app.assets.storage.Client", return_value=fake_storage_client):
                response = self.client.post(
                    "/api/v1/assets/signed-upload-url",
                    headers=bearer("editor-token"),
                    json={
                        "filename": "hero-image.png",
                        "mimeType": "image/png",
                        "expiresInSeconds": 120,
                    },
                )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["bucket"], "cms-dev-assets")
        self.assertEqual(payload["mimeType"], "image/png")
        self.assertEqual(payload["requiredHeaders"]["Content-Type"], "image/png")
        self.assertTrue(payload["objectPath"].startswith("uploads/"))
        self.assertEqual(payload["uploadUrl"], "https://storage.googleapis.com/upload-signed-url")

        self.assertEqual(fake_storage_client.bucket_name, "cms-dev-assets")
        self.assertEqual(fake_storage_client.blob.call_kwargs["method"], "PUT")
        self.assertEqual(fake_storage_client.blob.call_kwargs["content_type"], "image/png")
        self.assertEqual(fake_storage_client.blob.call_kwargs["version"], "v4")
        self.assertEqual(fake_storage_client.blob.call_kwargs["expiration"], timedelta(seconds=120))


if __name__ == "__main__":
    unittest.main()
