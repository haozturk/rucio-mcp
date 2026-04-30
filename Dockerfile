FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      voms-clients-java \
      ca-certificates \
      igtf-policy-classic \
 && rm -rf /var/lib/apt/lists/*

# CMS VOMS configuration: vomses describes the VOMS servers, vomsdir/*.lsc
# lists the expected VOMS server + issuing CA DNs. These are public CMS metadata.
# IGTF trust anchors (including the CERN Grid CA that signs CMS user certs)
# come from the igtf-policy-classic package above, populating
# /etc/grid-security/certificates.
COPY docker/vomses/ /etc/vomses/
COPY docker/vomsdir/ /etc/grid-security/vomsdir/

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY docker/entrypoint.sh /entrypoint.sh
RUN pip install --no-cache-dir . \
 && chmod +x /entrypoint.sh

ENV RUCIO_MCP_TRANSPORT=streamable-http
ENV RUCIO_MCP_HOST=0.0.0.0
ENV RUCIO_MCP_PORT=8000
ENV X509_USER_PROXY=/tmp/x509up

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
