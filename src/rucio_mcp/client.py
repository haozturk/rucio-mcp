from __future__ import annotations

from typing import Any

from .settings import RucioSettings


def create_rucio_client() -> Any:
    """Create a configured Rucio client from environment variables."""
    try:
        from rucio.client import Client
    except Exception as exc:  # pragma: no cover - runtime dependency guard
        raise RuntimeError(
            "Unable to import rucio client. Install dependency 'rucio-clients'."
        ) from exc

    settings = RucioSettings.from_env()

    kwargs: dict[str, Any] = {
        "rucio_host": settings.rucio_host,
        "auth_host": settings.auth_host,
        "account": settings.account,
        "auth_type": settings.auth_type,
        "timeout": settings.timeout,
    }
    if settings.vo:
        kwargs["vo"] = settings.vo
    if settings.ca_cert:
        kwargs["ca_cert"] = settings.ca_cert
    if settings.creds is not None:
        kwargs["creds"] = settings.creds

    return Client(**kwargs)
