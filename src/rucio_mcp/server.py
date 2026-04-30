from __future__ import annotations

import logging
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import create_rucio_client
from .service import RucioService

logger = logging.getLogger(__name__)

_host = os.environ.get("RUCIO_MCP_HOST", "0.0.0.0")
_port = int(os.environ.get("RUCIO_MCP_PORT", "8000"))
mcp = FastMCP("rucio-mcp", host=_host, port=_port)
service = RucioService(client_factory=create_rucio_client)


@mcp.tool()
def rucio_ping() -> dict[str, Any]:
    """Ping Rucio and return basic server information."""
    return service.ping()


@mcp.tool()
def rucio_whoami() -> dict[str, Any]:
    """Return account information for the active auth token."""
    return service.whoami()


@mcp.tool()
def rucio_list_dids(
    scope: str,
    name_pattern: str = "*",
    did_type: str = "collection",
    long: bool = False,
    recursive: bool = False,
    limit: int = 200,
) -> dict[str, Any]:
    """List DIDs in a scope using name pattern matching."""
    return service.list_dids(
        scope=scope,
        name_pattern=name_pattern,
        did_type=did_type,
        long=long,
        recursive=recursive,
        limit=limit,
    )


@mcp.tool()
def rucio_get_did(scope: str, name: str, dynamic_depth: str | None = None) -> dict[str, Any]:
    """Get a single DID by scope and name."""
    return service.get_did(scope=scope, name=name, dynamic_depth=dynamic_depth)


@mcp.tool()
def rucio_list_replicas(
    dids: list[dict[str, str]],
    schemes: list[str] | None = None,
    ignore_availability: bool = True,
    all_states: bool = False,
    rse_expression: str | None = None,
    resolve_archives: bool = True,
    limit: int = 200,
) -> dict[str, Any]:
    """List replicas for one or more DIDs."""
    return service.list_replicas(
        dids=dids,
        schemes=schemes,
        ignore_availability=ignore_availability,
        all_states=all_states,
        rse_expression=rse_expression,
        resolve_archives=resolve_archives,
        limit=limit,
    )


@mcp.tool()
def rucio_list_rses(rse_expression: str | None = None, limit: int = 200) -> dict[str, Any]:
    """List RSEs, optionally filtered by an RSE expression.

    Pass `null` (or omit) to list all RSEs.

    RSE expression syntax (NOT shell globs, NOT SQL):
      - Atoms are `key=value` pairs matched against RSE attributes, or a literal RSE name.
      - Combine with `&` (AND), `|` (OR), `\\` (EXCLUDE). Parentheses group.
      - Common attributes: `tier` (0/1/2/3), `country` (2-letter), `type` (DATADISK/SCRATCHDISK/...), `cms_type`.

    Examples:
      - `tier=1`                             → all Tier-1 RSEs
      - `tier=0|tier=1`                      → T0 and T1
      - `country=CH&tier=2`                  → Swiss T2 RSEs
      - `(tier=1|tier=2)\\tier=2_TEST`       → T1+T2 excluding test RSEs
      - `T1_US_FNAL_Disk`                    → exact RSE name

    Do NOT use shell glob patterns like `T1_*`. Use attribute-based filters instead.
    """
    return service.list_rses(rse_expression=rse_expression, limit=limit)


@mcp.tool()
def rucio_get_rse(rse: str) -> dict[str, Any]:
    """Get details for a single RSE."""
    return service.get_rse(rse=rse)


@mcp.tool()
def rucio_list_requests(
    src_rse: str,
    dst_rse: str,
    request_states: list[str],
    limit: int = 200,
) -> dict[str, Any]:
    """List transfer requests for source/destination RSEs and request states."""
    return service.list_requests(
        src_rse=src_rse,
        dst_rse=dst_rse,
        request_states=request_states,
        limit=limit,
    )


@mcp.tool()
def rucio_list_requests_history(
    src_rse: str,
    dst_rse: str,
    request_states: list[str],
    offset: int = 0,
    limit: int = 200,
) -> dict[str, Any]:
    """List historical transfer requests."""
    return service.list_requests_history(
        src_rse=src_rse,
        dst_rse=dst_rse,
        request_states=request_states,
        offset=offset,
        limit=limit,
    )


@mcp.tool()
def rucio_list_replication_rules(filters: dict[str, Any] | None = None, limit: int = 200) -> dict[str, Any]:
    """List replication rules using optional filters."""
    return service.list_replication_rules(filters=filters, limit=limit)


@mcp.tool()
def rucio_get_replication_rule(rule_id: str) -> dict[str, Any]:
    """Get one replication rule by id."""
    return service.get_replication_rule(rule_id=rule_id)


# ── DID content & metadata ────────────────────────────────────────────


@mcp.tool()
def rucio_list_content(scope: str, name: str, limit: int = 200) -> dict[str, Any]:
    """List the children of a dataset or container DID.

    Use this after `rucio_get_did` to see what's inside a collection — files in a
    dataset, or datasets in a container. Does not recurse; returns direct children only.
    """
    return service.list_content(scope=scope, name=name, limit=limit)


@mcp.tool()
def rucio_list_parent_dids(scope: str, name: str, limit: int = 200) -> dict[str, Any]:
    """List the parent DIDs that contain a given DID.

    Reverse lookup: given a file or dataset, find which datasets or containers
    reference it.
    """
    return service.list_parent_dids(scope=scope, name=name, limit=limit)


@mcp.tool()
def rucio_get_metadata(scope: str, name: str, plugin: str = "DID_COLUMN") -> dict[str, Any]:
    """Get metadata for a DID.

    `plugin` selects the metadata source. "DID_COLUMN" (default) returns core
    Rucio-managed fields. "JSON" returns custom user-set metadata. "ALL" merges both.
    """
    return service.get_metadata(scope=scope, name=name, plugin=plugin)


@mcp.tool()
def rucio_list_dataset_replicas(
    scope: str, name: str, deep: bool = False, limit: int = 200
) -> dict[str, Any]:
    """List replica locations at dataset granularity.

    Prefer this over `rucio_list_replicas` when you want to know "where is this
    dataset" rather than "where is each file." `deep=True` resolves archive datasets.
    """
    return service.list_dataset_replicas(scope=scope, name=name, deep=deep, limit=limit)


@mcp.tool()
def rucio_list_did_rules(scope: str, name: str, limit: int = 200) -> dict[str, Any]:
    """List replication rules that apply to a specific DID.

    Answers "why is this dataset replicated where it is." Complements
    `rucio_list_replication_rules` (which is global) by scoping to one DID.
    """
    return service.list_did_rules(scope=scope, name=name, limit=limit)


# ── RSE operational data ──────────────────────────────────────────────


@mcp.tool()
def rucio_get_rse_usage(
    rse: str, filters: dict[str, Any] | None = None, limit: int = 200
) -> dict[str, Any]:
    """Get current space usage for an RSE, broken down by source.

    Returns one entry per source (`rucio`, `storage`, `static`, etc.). Each entry
    reports used, free, and total bytes. Use to answer "how full is this RSE."
    """
    return service.get_rse_usage(rse=rse, filters=filters, limit=limit)


@mcp.tool()
def rucio_get_rse_limits(rse: str, limit: int = 200) -> dict[str, Any]:
    """Get the configured space limits for an RSE (e.g., min_free_space)."""
    return service.get_rse_limits(rse=rse, limit=limit)


@mcp.tool()
def rucio_list_rse_attributes(rse: str) -> dict[str, Any]:
    """Get the custom attributes of an RSE.

    Includes tier, country, continent, and any site-specific tags. Use to answer
    questions like "is this a Tier-1?" or "what country is this site in?"
    """
    return service.list_rse_attributes(rse=rse)


@mcp.tool()
def rucio_get_rse_protocols(rse: str) -> dict[str, Any]:
    """Get the transfer protocols supported by an RSE (gsiftp, davs, root, etc.)."""
    return service.get_rse_protocols(rse=rse)


@mcp.tool()
def rucio_get_distance(source: str, destination: str) -> dict[str, Any]:
    """Get the configured network distance from one RSE to another.

    Used by Rucio for transfer routing decisions. Lower distance = preferred path.
    """
    return service.get_distance(source=source, destination=destination)


@mcp.tool()
def rucio_list_transfer_limits(limit: int = 200) -> dict[str, Any]:
    """List transfer limit policies (concurrency caps and waiting limits per RSE).

    Useful for debugging "why are transfers throttled" — each entry describes a
    limit applied by RSE expression, activity, and direction.
    """
    return service.list_transfer_limits(limit=limit)


# ── Accounts & quotas ─────────────────────────────────────────────────


@mcp.tool()
def rucio_list_accounts(
    account_type: str | None = None,
    identity: str | None = None,
    filters: dict[str, Any] | None = None,
    limit: int = 200,
) -> dict[str, Any]:
    """List Rucio accounts.

    `account_type` is one of "USER", "SERVICE", "GROUP". `identity` filters to
    accounts linked to a specific identity string (e.g., an X509 DN).
    """
    return service.list_accounts(
        account_type=account_type, identity=identity, filters=filters, limit=limit
    )


@mcp.tool()
def rucio_get_account(account: str) -> dict[str, Any]:
    """Get details for a single account (status, email, type, created_at, etc.)."""
    return service.get_account(account=account)


@mcp.tool()
def rucio_get_local_account_usage(
    account: str, rse: str | None = None, limit: int = 200
) -> dict[str, Any]:
    """Get per-RSE storage usage for an account.

    Omit `rse` for usage across all RSEs. Pass `rse` to scope to one site.
    Answers "how much has account X stored at site Y."
    """
    return service.get_local_account_usage(account=account, rse=rse, limit=limit)


@mcp.tool()
def rucio_get_local_account_limits(account: str) -> dict[str, Any]:
    """Get per-RSE quota limits for an account."""
    return service.get_local_account_limits(account=account)


@mcp.tool()
def rucio_list_account_rules(account: str, limit: int = 200) -> dict[str, Any]:
    """List replication rules owned by an account."""
    return service.list_account_rules(account=account, limit=limit)


# ── Subscriptions ─────────────────────────────────────────────────────


@mcp.tool()
def rucio_list_subscriptions(
    name: str | None = None, account: str | None = None, limit: int = 200
) -> dict[str, Any]:
    """List subscriptions (auto-rule-generating policies).

    Pass `name` and/or `account` to narrow to a specific subscription. With both
    set to exact values, returns one subscription's details.
    """
    return service.list_subscriptions(name=name, account=account, limit=limit)


@mcp.tool()
def rucio_list_subscription_rules(account: str, name: str, limit: int = 200) -> dict[str, Any]:
    """List replication rules produced by a specific subscription.

    Use to investigate whether a subscription is generating rules as expected.
    """
    return service.list_subscription_rules(account=account, name=name, limit=limit)


# ── Locks ─────────────────────────────────────────────────────────────


@mcp.tool()
def rucio_get_dataset_locks(scope: str, name: str, limit: int = 200) -> dict[str, Any]:
    """List locks on a dataset (which rules keep its replicas pinned and where)."""
    return service.get_dataset_locks(scope=scope, name=name, limit=limit)


@mcp.tool()
def rucio_get_dataset_locks_by_rse(rse: str, limit: int = 200) -> dict[str, Any]:
    """List all dataset locks at a given RSE. Answers "what's locked on this site."""
    return service.get_dataset_locks_by_rse(rse=rse, limit=limit)


# ── Scopes ────────────────────────────────────────────────────────────


@mcp.tool()
def rucio_list_scopes() -> dict[str, Any]:
    """List all scopes on the Rucio instance.

    Useful when the agent doesn't know which scope a DID belongs to.
    """
    return service.list_scopes()


@mcp.tool()
def rucio_list_scopes_for_account(account: str) -> dict[str, Any]:
    """List scopes that a specific account can write to."""
    return service.list_scopes_for_account(account=account)


def main() -> None:
    # Logs go to stderr; stdio transport uses stdout for protocol messages.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        stream=sys.stderr,
    )
    transport = os.environ.get("RUCIO_MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        logger.info("Starting rucio-mcp server over streamable-http on %s:%s", _host, _port)
    else:
        logger.info("Starting rucio-mcp server over %s", transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
