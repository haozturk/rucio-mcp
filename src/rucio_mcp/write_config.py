"""Write a minimal rucio.cfg from environment variables.

The Rucio client library requires a config file on disk even when all
connection parameters are passed programmatically. This module reads
RUCIO_* env vars and writes /tmp/rucio.cfg with a [client] section.
"""
from __future__ import annotations

import configparser
import os
import sys

CONFIG_PATH = "/tmp/rucio.cfg"


def build_config() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()

    client: dict[str, str] = {}
    for env_key, cfg_key in [
        ("RUCIO_HOST", "rucio_host"),
        ("RUCIO_AUTH_HOST", "auth_host"),
        ("RUCIO_ACCOUNT", "account"),
        ("RUCIO_AUTH_TYPE", "auth_type"),
        ("RUCIO_CA_CERT", "ca_cert"),
        ("X509_USER_PROXY", "client_x509_proxy"),
        ("RUCIO_VO", "vo"),
    ]:
        value = os.environ.get(env_key, "").strip()
        if value:
            client[cfg_key] = value

    if not client.get("rucio_host"):
        raise RuntimeError("RUCIO_HOST is required but not set in the environment")

    cfg["client"] = client
    return cfg


def write(path: str = CONFIG_PATH) -> str:
    cfg = build_config()
    with open(path, "w") as f:
        cfg.write(f)
    return path


def main() -> int:
    try:
        path = write()
    except RuntimeError as exc:
        print(f"rucio_mcp.write_config: {exc}", file=sys.stderr)
        return 1
    print(f"rucio_mcp.write_config: wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
