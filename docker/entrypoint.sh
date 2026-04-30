#!/bin/bash
set -euo pipefail

: "${X509_USER_PROXY:=/tmp/x509up}"
# VOMS attribute extension is OFF by default. Enable by setting VOMS=cms (or
# another VO) — note this requires network access to the VOMS server, which
# isn't available from all hosts. Basic RFC proxies (no VOMS) are sufficient
# for Rucio x509_proxy auth in most deployments.
: "${VOMS:=}"
: "${VOMS_VALID:=192:00}"
: "${PROXY_REFRESH_SECONDS:=21600}"
GLOBUS_DIR="${GLOBUS_DIR:-/root/.globus}"

init_proxy() {
    local args=(-rfc -valid "$VOMS_VALID"
                -cert "$GLOBUS_DIR/usercert.pem"
                -key  "$GLOBUS_DIR/userkey.pem"
                -out  "$X509_USER_PROXY"
                --pwstdin)
    if [[ -n "$VOMS" ]]; then
        args+=(-voms "$VOMS")
    fi
    voms-proxy-init "${args[@]}" < /dev/null
}

# Three modes:
#   1. GLOBUS_DIR has usercert+userkey → generate proxy + auto-refresh
#   2. X509_USER_PROXY points to an existing valid file → use as-is (no refresh)
#   3. Neither → fail fast
if [[ -f "$GLOBUS_DIR/usercert.pem" && -f "$GLOBUS_DIR/userkey.pem" ]]; then
    echo "[entrypoint] generating proxy from $GLOBUS_DIR"
    init_proxy
    (
        while sleep "$PROXY_REFRESH_SECONDS"; do
            init_proxy || echo "[entrypoint] proxy renewal failed" >&2
        done
    ) &
elif [[ -f "$X509_USER_PROXY" && -s "$X509_USER_PROXY" ]]; then
    echo "[entrypoint] using pre-existing proxy at $X509_USER_PROXY (no auto-refresh)"
else
    echo "[entrypoint] ERROR: no credentials found." >&2
    echo "[entrypoint] Mount either $GLOBUS_DIR (with usercert.pem + userkey.pem)" >&2
    echo "[entrypoint] or a valid proxy file at $X509_USER_PROXY." >&2
    exit 1
fi

python -m rucio_mcp.write_config
export RUCIO_CONFIG=/tmp/rucio.cfg

exec rucio-mcp
