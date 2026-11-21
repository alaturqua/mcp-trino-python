# Remote and Docker deployment

By default each user's AI client starts its own copy of the server (the `stdio` transport). To share one server, for
example for a team or a web client, run it over HTTP.

## Run over HTTP

```bash
uvx mcp-trino-python --transport http --host 0.0.0.0 --port 8000
```

- MCP endpoint: `http://<host>:8000/mcp` (Streamable HTTP)
- Health check: `http://<host>:8000/health`

Connect a client to it, for example in Claude Code:

```bash
claude mcp add --transport http trino http://localhost:8000/mcp
```

!!! danger "There is no authentication on the HTTP endpoint"
    Anyone who can reach the port can run queries as `TRINO_USER`. Keep it on a private network or put it behind a
    proxy that authenticates users, and consider [read-only mode](configuration.md#read-only-mode).

## Docker

The image is `ghcr.io/alaturqua/mcp-trino-python`. Tags follow the releases (`0.8.0`, `0.8`, `latest`).

```bash
# Streamable HTTP on port 8000
docker run --rm -p 8000:8000 \
  -e TRINO_HOST=trino.example.com -e TRINO_USER=analyst \
  ghcr.io/alaturqua/mcp-trino-python --transport http
```

Without arguments the container uses `stdio`, which is what MCP clients expect when they start it themselves.

## Docker Compose

The repository's `docker-compose.yml` starts Trino with sample data plus the server on port 8000:

```bash
git clone https://github.com/alaturqua/mcp-trino-python.git
cd mcp-trino-python
docker compose up
```

Then connect your client to `http://localhost:8000/mcp`.

## Legacy SSE

Some older clients only support the SSE transport. Use `--transport sse`; the endpoint is then `/sse`.
New setups should use `http`.
