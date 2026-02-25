from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from google.cloud import storage
from pydantic import BaseModel, ConfigDict, Field

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/avif",
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/webp",
    "video/mp4",
}

_FILENAME_SANITIZER = re.compile(r"[^a-zA-Z0-9._-]+")


class SignedUploadUrlRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    filename: str = Field(min_length=1, max_length=256)
    mime_type: str = Field(alias="mimeType", min_length=1)
    expires_in_seconds: int = Field(alias="expiresInSeconds", default=900, ge=60, le=3600)


class SignedUploadUrlResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    upload_url: str = Field(alias="uploadUrl")
    bucket: str
    object_path: str = Field(alias="objectPath")
    mime_type: str = Field(alias="mimeType")
    expires_at: str = Field(alias="expiresAt")
    required_headers: dict[str, str] = Field(alias="requiredHeaders")


def _assets_bucket_name() -> str:
    bucket = os.getenv("CMS_ASSETS_BUCKET", "").strip()
    if bucket:
        return bucket
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="CMS_ASSETS_BUCKET is not configured.",
    )


def _validate_mime_type(mime_type: str) -> str:
    normalized = mime_type.strip().lower()
    if normalized in ALLOWED_MIME_TYPES:
        return normalized

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            "Unsupported mime type. "
            f"Allowed types: {sorted(ALLOWED_MIME_TYPES)}."
        ),
    )


def _safe_object_name(filename: str) -> str:
    cleaned = _FILENAME_SANITIZER.sub("-", filename.strip())
    cleaned = cleaned.strip(".-")
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is invalid after sanitization.",
        )

    now = datetime.now(timezone.utc)
    return f"uploads/{now:%Y/%m/%d}/{uuid4().hex}-{cleaned[:120]}"


def create_signed_upload_url(payload: SignedUploadUrlRequest) -> SignedUploadUrlResponse:
    bucket_name = _assets_bucket_name()
    mime_type = _validate_mime_type(payload.mime_type)
    object_path = _safe_object_name(payload.filename)

    expires_delta = timedelta(seconds=payload.expires_in_seconds)
    expires_at = datetime.now(timezone.utc) + expires_delta

    blob = storage.Client().bucket(bucket_name).blob(object_path)
    upload_url = blob.generate_signed_url(
        version="v4",
        expiration=expires_delta,
        method="PUT",
        content_type=mime_type,
    )

    return SignedUploadUrlResponse(
        upload_url=upload_url,
        bucket=bucket_name,
        object_path=object_path,
        mime_type=mime_type,
        expires_at=expires_at.isoformat(),
        required_headers={"Content-Type": mime_type},
    )
