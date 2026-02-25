# EPIC-1 / US-1.3 - Secure storage and upload paths

## Story

As a security engineer, I want uploads restricted via signed URLs so that no public write path exists.

## Implementation in this repository

- Signed upload endpoint:
  - `POST /api/v1/assets/signed-upload-url`
  - Implemented in `app/main.py`
- Signed URL generation and validation:
  - `app/assets.py`
  - Uses Google Cloud Storage V4 signed URLs (`PUT`)
  - Enforces MIME allow-list
  - Enforces signed URL expiration window (`60` to `3600` seconds)
- Automated tests:
  - `tests/test_signed_upload.py`

## Configuration

```bash
export CMS_ASSETS_BUCKET="cms-dev-assets"
```

## Acceptance criteria mapping

- [x] `POST /assets/signed-upload-url` implemented.
- [x] GCS buckets private by default (Terraform `public_access_prevention = "enforced"`).
- [x] Signed upload expires and enforces mime restrictions.
