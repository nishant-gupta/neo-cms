#!/usr/bin/env python3
"""Bootstrap Firestore collections for EPIC-1 US-1.1.

Firestore collections are created implicitly when documents are created.
This utility creates (or optionally removes) a sentinel document in each
required collection.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Iterable

DEFAULT_COLLECTIONS = ("pages", "assets", "revisions")
SENTINEL_DOC_ID = "__bootstrap__"


def get_access_token() -> str:
    """Reads an access token from the local gcloud session."""
    cmd = ["gcloud", "auth", "print-access-token"]
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("gcloud CLI is required but was not found in PATH.") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip()
        raise RuntimeError(f"Unable to read access token from gcloud: {stderr}") from exc

    token = result.stdout.strip()
    if not token:
        raise RuntimeError("gcloud returned an empty access token.")
    return token


def firestore_base(project_id: str) -> str:
    return f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents"


def request_json(method: str, url: str, token: str, payload: dict | None = None) -> tuple[int, dict]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, method=method, data=body)
    req.add_header("Authorization", f"Bearer {token}")
    if body is not None:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read().decode("utf-8") or "{}"
            return response.status, json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8") or "{}"
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        return exc.code, parsed


def bootstrap_collection(project_id: str, collection: str, token: str) -> None:
    encoded_collection = urllib.parse.quote(collection, safe="")
    encoded_doc_id = urllib.parse.quote(SENTINEL_DOC_ID, safe="")
    url = f"{firestore_base(project_id)}/{encoded_collection}?documentId={encoded_doc_id}"

    payload = {
        "fields": {
            "bootstrap": {"booleanValue": True},
            "createdAt": {"timestampValue": datetime.now(timezone.utc).isoformat()},
        }
    }
    status, data = request_json("POST", url, token, payload=payload)

    if status in (200, 201):
        print(f"[created] {collection}/{SENTINEL_DOC_ID}")
        return
    if status == 409:
        print(f"[exists]  {collection}/{SENTINEL_DOC_ID}")
        return

    raise RuntimeError(
        f"Failed bootstrapping {collection}. "
        f"HTTP {status} response: {json.dumps(data, indent=2)}"
    )


def cleanup_collection(project_id: str, collection: str, token: str) -> None:
    encoded_collection = urllib.parse.quote(collection, safe="")
    encoded_doc_id = urllib.parse.quote(SENTINEL_DOC_ID, safe="")
    url = f"{firestore_base(project_id)}/{encoded_collection}/{encoded_doc_id}"

    status, data = request_json("DELETE", url, token)
    if status in (200, 204):
        print(f"[deleted] {collection}/{SENTINEL_DOC_ID}")
        return
    if status == 404:
        print(f"[missing] {collection}/{SENTINEL_DOC_ID}")
        return

    raise RuntimeError(
        f"Failed cleaning up {collection}. "
        f"HTTP {status} response: {json.dumps(data, indent=2)}"
    )


def parse_collections(raw_collections: str | None) -> Iterable[str]:
    if not raw_collections:
        return DEFAULT_COLLECTIONS
    items = [item.strip() for item in raw_collections.split(",")]
    return tuple(item for item in items if item)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap Firestore collections for CMS v1.")
    parser.add_argument(
        "--project-id",
        default=os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCLOUD_PROJECT"),
        help="GCP project ID (defaults to GOOGLE_CLOUD_PROJECT/GCLOUD_PROJECT).",
    )
    parser.add_argument(
        "--collections",
        default=None,
        help="Comma-separated collection names. Defaults to pages,assets,revisions.",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete sentinel docs instead of creating them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.project_id:
        print(
            "error: --project-id is required when GOOGLE_CLOUD_PROJECT is not set.",
            file=sys.stderr,
        )
        return 2

    collections = tuple(parse_collections(args.collections))
    if not collections:
        print("error: no collections were provided.", file=sys.stderr)
        return 2

    try:
        token = get_access_token()
        if args.cleanup:
            for collection in collections:
                cleanup_collection(args.project_id, collection, token)
        else:
            for collection in collections:
                bootstrap_collection(args.project_id, collection, token)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
