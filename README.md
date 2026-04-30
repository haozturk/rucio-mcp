# rucio-mcp

Read-only MCP server exposing selected Rucio client APIs. Speaks **stdio** (default)
and **streamable HTTP**, ships as a Docker image with optional X509 proxy
auto-renewal.

## Features

- 33 read-only tools across DIDs, replicas, RSEs, transfers, rules, accounts,
  subscriptions, locks, and scopes
- Two transports: stdio for in-process agents, streamable HTTP for sidecar
  deployments
- Docker image bundles `voms-clients-java` and IGTF trust anchors so it can
  generate its own X509 proxies given a mounted user cert + key
- Environment-driven configuration (Rucio endpoints, account, auth type)
- Tool responses normalized for agent consumption (`{status, count, truncated, items}`
  for lists, `{status, data}` for singletons)

## Quick start

### Local (stdio)

```bash
pip install -e .
RUCIO_HOST=http://cms-rucio.cern.ch \
RUCIO_AUTH_HOST=https://cms-rucio-auth.cern.ch \
RUCIO_ACCOUNT=<your-account> \
RUCIO_AUTH_TYPE=x509_proxy \
X509_USER_PROXY=/tmp/x509up_u$(id -u) \
rucio-mcp
```

### Docker (streamable HTTP)

```bash
docker build -t rucio-mcp .

docker run --rm \
  -v $HOME/.globus:/root/.globus:ro \
  -p 8000:8000 \
  -e RUCIO_HOST=http://cms-rucio.cern.ch \
  -e RUCIO_AUTH_HOST=https://cms-rucio-auth.cern.ch \
  -e RUCIO_ACCOUNT=<your-account> \
  -e RUCIO_AUTH_TYPE=x509_proxy \
  rucio-mcp
```

The container's entrypoint will detect `~/.globus/{usercert,userkey}.pem`,
generate a proxy at `/tmp/x509up`, and refresh it every 6 hours. After a few
seconds, `POST http://localhost:8000/mcp` accepts MCP protocol messages.

## Transports

Selected via `RUCIO_MCP_TRANSPORT`:

| Value | When to use |
|---|---|
| `stdio` (default for `pip install`) | Spawn as a subprocess from a Python agent (`langchain-mcp-adapters`, etc.) |
| `streamable-http` (default in the Docker image) | Run as a standalone HTTP server (sidecar pattern). Listens on `RUCIO_MCP_HOST:RUCIO_MCP_PORT` (defaults `0.0.0.0:8000`). |

## Environment variables

### Rucio connection

| Variable | Default | Notes |
|---|---|---|
| `RUCIO_HOST` | — | Required. Rucio API endpoint (e.g. `http://cms-rucio.cern.ch`). |
| `RUCIO_AUTH_HOST` | — | Required. Rucio auth endpoint. |
| `RUCIO_ACCOUNT` | — | Required. Rucio account name to authenticate as. |
| `RUCIO_AUTH_TYPE` | `oidc` | `x509_proxy` or `oidc`. |
| `RUCIO_VO` | unset | VO scope (rarely needed for single-VO instances). |
| `RUCIO_TIMEOUT` | `600` | Client request timeout in seconds. |
| `RUCIO_CA_CERT` | unset | Path to CA bundle for HTTPS verification. |
| `RUCIO_CREDS_JSON` | unset | JSON object of additional client credentials. |

### Server / transport

| Variable | Default | Notes |
|---|---|---|
| `RUCIO_MCP_TRANSPORT` | `stdio` (image overrides to `streamable-http`) | Wire transport. |
| `RUCIO_MCP_HOST` | `0.0.0.0` | Bind address (HTTP only). |
| `RUCIO_MCP_PORT` | `8000` | Bind port (HTTP only). |

### X509 proxy lifecycle (Docker only)

| Variable | Default | Notes |
|---|---|---|
| `X509_USER_PROXY` | `/tmp/x509up` | Where the generated proxy is written. |
| `GLOBUS_DIR` | `/root/.globus` | Where to look for `usercert.pem` + `userkey.pem`. |
| `VOMS_VALID` | `192:00` | Proxy validity window (HH:MM). |
| `PROXY_REFRESH_SECONDS` | `21600` (6h) | Background refresh interval. |
| `VOMS` | unset | Set to e.g. `cms` to add VOMS attributes (requires network access to the VOMS server). Without it, the entrypoint generates a basic RFC proxy locally. |

The entrypoint runs in one of three modes depending on what's mounted:

1. `~/.globus/usercert.pem` + `~/.globus/userkey.pem` present → generate proxy + start a 6h refresh loop in the background.
2. A valid proxy file already at `$X509_USER_PROXY` → use as-is, no refresh.
3. Neither → fail fast with a clear error.

## Tools

All tools are read-only. List endpoints accept `limit` (default 200, capped at
1000) and return `{status, count, truncated, items}`. Singleton endpoints return
`{status, data}`.

### Identity & connection

- `rucio_ping`
- `rucio_whoami`

### DIDs

- `rucio_list_dids` — list DIDs in a scope by name pattern
- `rucio_get_did` — get a single DID by scope+name
- `rucio_list_content` — children of a dataset/container
- `rucio_list_parent_dids` — parents of a DID (reverse lookup)
- `rucio_get_metadata` — DID metadata (`plugin`: `DID_COLUMN`, `JSON`, `ALL`)
- `rucio_list_did_rules` — rules attached to a specific DID

### Replicas

- `rucio_list_replicas` — file-level replica locations
- `rucio_list_dataset_replicas` — dataset-level replica locations

### RSEs

- `rucio_list_rses` — list RSEs by RSE expression (e.g. `tier=1&country=DE`)
- `rucio_get_rse` — RSE details
- `rucio_get_rse_usage` — current space usage per source
- `rucio_get_rse_limits` — configured space limits
- `rucio_list_rse_attributes` — custom attributes (tier, country, type, …)
- `rucio_get_rse_protocols` — supported transfer protocols
- `rucio_get_distance` — RSE-to-RSE network distance
- `rucio_list_transfer_limits` — transfer-limit policies

### Requests (transfers)

- `rucio_list_requests` — current transfer requests
- `rucio_list_requests_history` — historical transfer requests (offset/limit pagination)

### Rules

- `rucio_list_replication_rules` — list rules with optional filters
- `rucio_get_replication_rule` — rule by id

### Accounts & quotas

- `rucio_list_accounts`
- `rucio_get_account`
- `rucio_get_local_account_usage` — per-RSE storage used by an account
- `rucio_get_local_account_limits` — per-RSE quota caps
- `rucio_list_account_rules` — rules owned by an account

### Subscriptions

- `rucio_list_subscriptions`
- `rucio_list_subscription_rules` — rules generated by a subscription

### Locks

- `rucio_get_dataset_locks` — locks on a specific dataset
- `rucio_get_dataset_locks_by_rse` — all dataset locks at an RSE

### Scopes

- `rucio_list_scopes`
- `rucio_list_scopes_for_account`

## Authentication notes

### X509 proxy

The default. Provide a valid grid proxy via `X509_USER_PROXY` (or let the
container generate one from `~/.globus`). Rucio identifies the user by the DN
in the cert chain.

### OIDC

Set `RUCIO_AUTH_TYPE=oidc`. Requires CMS IAM (or your VO's IAM) to have an OIDC
client registered for the account, plus a corresponding entry in Rucio's
identity table. With OIDC enabled, no proxy plumbing is needed — the X509
mounts and the proxy refresher become unused.

## Development

```bash
pip install -e ".[dev]"
pytest
```

The package layout is intentionally thin: `server.py` declares MCP tools,
`service.py` wraps the Rucio Python client and shapes responses, `client.py`
constructs the Rucio client from environment variables, `write_config.py`
materializes a minimal `rucio.cfg` from environment so the underlying Rucio
client library can load.
