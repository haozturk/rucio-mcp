from __future__ import annotations

import logging
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import create_rucio_client
from .service import RucioService

logger = logging.getLogger(__name__)

mcp = FastMCP("rucio-mcp")
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
    """List RSEs, optionally filtered by expression."""
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


def main() -> None:
    # MCP protocol messages must go to stdout; logs must go to stderr.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        stream=sys.stderr,
    )
    logger.info("Starting rucio-mcp server over stdio")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
