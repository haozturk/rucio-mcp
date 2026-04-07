# rucio-mcp

Read-only MCP server exposing selected Rucio client APIs over stdio.

## Features

- Environment-based authentication and connection setup
- Read-only tools for identity, DIDs, replicas, RSEs, requests, and rules
- Tool responses normalized for agent consumption

## Environment Variables

Required:
- `RUCIO_HOST`
- `RUCIO_AUTH_HOST`
- `RUCIO_ACCOUNT`

Optional:
- `RUCIO_AUTH_TYPE` (default: `oidc`)
- `RUCIO_VO`
- `RUCIO_TIMEOUT` (default: `600`)
- `RUCIO_CA_CERT`
- `RUCIO_CREDS_JSON` (JSON object)

## Install (editable)

```bash
pip install -e .
```

## Run (stdio)

```bash
rucio-mcp
```

## V1 Tools

- `rucio_ping`
- `rucio_whoami`
- `rucio_list_dids`
- `rucio_get_did`
- `rucio_list_replicas`
- `rucio_list_rses`
- `rucio_get_rse`
- `rucio_list_requests`
- `rucio_list_requests_history`
- `rucio_list_replication_rules`
- `rucio_get_replication_rule`
