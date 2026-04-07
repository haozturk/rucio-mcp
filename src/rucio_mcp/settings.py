from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RucioSettings:
    rucio_host: str
    auth_host: str
    account: str
    auth_type: str = "oidc"
    vo: str | None = None
    timeout: int = 600
    ca_cert: str | None = None
    creds: dict[str, Any] | None = None

    @staticmethod
    def from_env() -> "RucioSettings":
        rucio_host = os.environ.get("RUCIO_HOST", "").strip()
        auth_host = os.environ.get("RUCIO_AUTH_HOST", "").strip()
        account = os.environ.get("RUCIO_ACCOUNT", "").strip()

        missing = [
            name
            for name, value in (
                ("RUCIO_HOST", rucio_host),
                ("RUCIO_AUTH_HOST", auth_host),
                ("RUCIO_ACCOUNT", account),
            )
            if not value
        ]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        auth_type = os.environ.get("RUCIO_AUTH_TYPE", "oidc").strip() or "oidc"
        vo = os.environ.get("RUCIO_VO") or None

        timeout_str = os.environ.get("RUCIO_TIMEOUT", "600")
        try:
            timeout = int(timeout_str)
        except ValueError as exc:
            raise ValueError("RUCIO_TIMEOUT must be an integer") from exc

        ca_cert = os.environ.get("RUCIO_CA_CERT") or None

        creds_json = os.environ.get("RUCIO_CREDS_JSON", "").strip()
        creds: dict[str, Any] | None = None
        if creds_json:
            try:
                parsed = json.loads(creds_json)
            except json.JSONDecodeError as exc:
                raise ValueError("RUCIO_CREDS_JSON must be valid JSON") from exc
            if not isinstance(parsed, dict):
                raise ValueError("RUCIO_CREDS_JSON must decode to a JSON object")
            creds = parsed

        return RucioSettings(
            rucio_host=rucio_host,
            auth_host=auth_host,
            account=account,
            auth_type=auth_type,
            vo=vo,
            timeout=timeout,
            ca_cert=ca_cert,
            creds=creds,
        )
