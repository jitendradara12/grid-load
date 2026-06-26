#!/usr/bin/env python3
"""Check Kaggle credentials locally without creating a dataset version.

This script tests the same auth path used by the Kaggle CLI and then probes the
blob-upload authorization endpoint that fails in GitHub Actions before any real
`kaggle datasets version` mutation happens.

It never prints token/key values.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.blobs.types.blob_api_service import ApiBlobType, ApiStartBlobUploadRequest

DATASET_REF = "jitendradara12/demand-met-from-sep25"


def _mask(value: str | None) -> str:
    if not value:
        return "missing"
    if len(value) <= 8:
        return "present(length<=8)"
    return f"present(length={len(value)}, suffix=...{value[-4:]})"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        print(f"FAIL: {path} exists but is invalid JSON: {exc}")
        sys.exit(2)


def print_credential_sources() -> None:
    home = Path.home()
    kaggle_json = home / ".kaggle" / "kaggle.json"
    access_token = home / ".kaggle" / "access_token"
    credentials_json = home / ".kaggle" / "credentials.json"

    print("Credential sources found:")
    print(f"- KAGGLE_USERNAME env: {_mask(os.environ.get('KAGGLE_USERNAME'))}")
    print(f"- KAGGLE_KEY env:      {_mask(os.environ.get('KAGGLE_KEY'))}")
    print(f"- KAGGLE_API_TOKEN env:{_mask(os.environ.get('KAGGLE_API_TOKEN'))}")
    print(f"- {kaggle_json}: {'exists' if kaggle_json.exists() else 'missing'}")
    print(f"- {access_token}: {'exists' if access_token.exists() else 'missing'}")
    print(f"- {credentials_json}: {'exists' if credentials_json.exists() else 'missing'}")

    data = _read_json(kaggle_json)
    if data is not None:
        print("kaggle.json fields:")
        print(f"- username: {data.get('username', 'missing')}")
        print(f"- key:      {_mask(data.get('key'))}")
        extra = sorted(set(data) - {"username", "key"})
        if extra:
            print(f"- extra fields: {extra}")


def main() -> int:
    print_credential_sources()
    print()

    api = KaggleApi()

    try:
        api.authenticate()
    except SystemExit as exc:
        print("FAIL: KaggleApi.authenticate() exited. No usable credentials were found.")
        return int(exc.code or 1)
    except Exception as exc:
        print(f"FAIL: KaggleApi.authenticate() raised {type(exc).__name__}: {exc}")
        return 1

    user = api.config_values.get("username") or api.config_values.get("user") or "unknown"
    auth_method = api.config_values.get("auth_method", "unknown")
    print(f"PASS: authenticate() succeeded as user={user!r}, auth_method={auth_method!r}")

    try:
        files = api.dataset_list_files(DATASET_REF).files or []
        file_names = [getattr(file, "name", str(file)) for file in files]
        print(f"PASS: can read dataset files for {DATASET_REF}: {file_names[:5]}")
    except Exception as exc:
        print(f"FAIL: authenticated, but cannot read dataset {DATASET_REF}: {type(exc).__name__}: {exc}")
        return 1

    # This probes the exact backend endpoint that your GitHub Action fails at:
    # https://www.kaggle.com/api/v1/blobs/upload
    # It starts an upload session for a fake 1-byte dataset blob but does NOT
    # call the returned upload URL and does NOT create a dataset version.
    try:
        req = ApiStartBlobUploadRequest()
        req.type = ApiBlobType.DATASET
        req.name = f"kaggle-auth-probe-{int(time.time())}.txt"
        req.content_length = 1
        req.last_modified_epoch_seconds = int(time.time())
        req.content_type = "text/plain"

        with api.build_kaggle_client() as client:
            response = client.blobs.blob_api_client.start_blob_upload(req)

        token = getattr(response, "token", None)
        create_url = getattr(response, "create_url", None)
        if token and create_url:
            print("PASS: blob upload authorization endpoint accepted these credentials.")
            print("      This means the local credentials can reach the endpoint that fails in GitHub Actions.")
            return 0

        print("WARN: blob endpoint returned without an error, but response looked incomplete.")
        print(f"      response={response}")
        return 1
    except Exception as exc:
        print(f"FAIL: blob upload authorization probe failed: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
