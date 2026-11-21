# MCP Trino Server

<!-- mcp-name: io.github.alaturqua/mcp-trino-python -->

[![PyPI](https://img.shields.io/pypi/v/mcp-trino-python?style=flat-square)](https://pypi.org/project/mcp-trino-python/)
[![Docs](https://img.shields.io/badge/docs-online-indigo?style=flat-square)](https://alaturqua.github.io/mcp-trino-python/)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://github.com/alaturqua/mcp-trino-python/pkgs/container/mcp-trino-python)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square)](https://opensource.org/licenses/Apache-2.0)
[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/alaturqua-mcp-trino-python-badge.png)](https://mseep.ai/app/alaturqua-mcp-trino-python)

**Let your AI assistant talk to [Trino](https://trino.io).** Ask questions about your data in plain language; the
assistant explores catalogs, writes and runs SQL, and inspects or maintains your Iceberg tables.

Works with Claude Code, Claude Desktop, GitHub Copilot in VS Code, Cursor, and any other
[MCP](https://modelcontextprotocol.io) client.

📖 **[Documentation](https://alaturqua.github.io/mcp-trino-python/)**

## Quick start

You need [uv](https://docs.astral.sh/uv/getting-started/installation/) and a Trino server
(or `docker run -d -p 8080:8080 trinodb/trino:484` for one with sample data).

### Claude Code

```bash
claude mcp add trino -e TRINO_HOST=localhost -e TRINO_USER=trino -- uvx mcp-trino-python
```

or install the plugin, which asks for the connection settings:

```text
/plugin marketplace add alaturqua/mcp-trino-python
/plugin install trino@mcp-trino-python
```

### Claude Desktop

Download `mcp-trino-python.mcpb` from the
[latest release](https://github.com/alaturqua/mcp-trino-python/releases/latest) and double-click it.

### VS Code / GitHub Copilot, Cursor and others

Add this to your client's MCP config
(`.vscode/mcp.json` uses `"servers"` instead of `"mcpServers"`):

```json
{
  "mcpServers": {
    "trino": {
      "command": "uvx",
      "args": ["mcp-trino-python"],
      "env": { "TRINO_HOST": "localhost", "TRINO_PORT": "8080", "TRINO_USER": "trino" }
    }
  }
}
```

Then ask: *"What catalogs are in Trino?"*

More clients, Docker and troubleshooting: **[Connect your AI client](https://alaturqua.github.io/mcp-trino-python/clients/)**.

## What it can do

- **Explore**: catalogs, schemas, tables, columns, DDL and statistics
- **Query**: run SQL and get the rows back as JSON
- **Iceberg**: snapshots, manifests, partitions, files, history, branches and tags
- **Maintain Iceberg tables**: compact files and manifests, expire old snapshots
- **Read-only mode**: `TRINO_READ_ONLY=true` blocks writes and hides maintenance tools

See the full [tool list](https://alaturqua.github.io/mcp-trino-python/tools/).

## Configuration

| Variable            | What it does                                     | Default     |
| ------------------- | ------------------------------------------------ | ----------- |
| `TRINO_HOST`        | Trino server hostname                            | `localhost` |
| `TRINO_PORT`        | Trino server port                                | `8080`      |
| `TRINO_USER`        | User to run queries as                           | `trino`     |
| `TRINO_PASSWORD`    | Password; turns on basic auth (needs https)      | not set     |
| `TRINO_HTTP_SCHEME` | `http` or `https`                                | `http`      |
| `TRINO_CATALOG`     | Default catalog                                  | not set     |
| `TRINO_SCHEMA`      | Default schema                                   | not set     |
| `TRINO_READ_ONLY`   | `true` blocks writes and hides maintenance tools | `false`     |

Running a shared server over HTTP or in Docker: see
[Remote and Docker deployment](https://alaturqua.github.io/mcp-trino-python/deployment/).

## Contributing

```bash
uv sync
docker compose up -d --wait trino
uv run pytest
```

See [Development](https://alaturqua.github.io/mcp-trino-python/development/) for linting, docs and releases.

## License

Apache 2.0. See [LICENSE](LICENSE).
