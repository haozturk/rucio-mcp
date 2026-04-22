FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      voms-clients-java \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

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
