# MCP Trino Server

<!-- mcp-name: io.github.alaturqua/mcp-trino-python -->

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/alaturqua-mcp-trino-python-badge.png)](https://mseep.ai/app/alaturqua-mcp-trino-python)
[![PyPI](https://img.shields.io/pypi/v/mcp-trino-python?style=flat-square)](https://pypi.org/project/mcp-trino-python/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-available-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://github.com/alaturqua/mcp-trino-python/pkgs/container/mcp-trino-python)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square)](https://opensource.org/licenses/Apache-2.0)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server for [Trino](https://trino.io),
built on [FastMCP](https://gofastmcp.com). It lets AI assistants explore catalogs, run SQL, and inspect or maintain
Iceberg tables.

- Discover catalogs, schemas, tables and views; describe tables and show DDL and stats
- Run SQL with JSON results
- Inspect Iceberg metadata (snapshots, manifests, partitions, files, refs, history)
- Iceberg maintenance (`optimize`, `optimize_manifests`, `expire_snapshots`)
- **Read-only mode** (`TRINO_READ_ONLY=true`) for safe exploration
- stdio and Streamable HTTP transports, Docker image, MCP Registry and Claude Code plugin

## Install

The server is published on PyPI and runs with [uv](https://docs.astral.sh/uv/), so there is nothing to clone:

```bash
uvx mcp-trino-python            # stdio
uvx mcp-trino-python --transport http --port 8000   # Streamable HTTP on http://localhost:8000/mcp
```

### Claude Code

Install the plugin from this repository's marketplace; Claude Code asks for the Trino connection settings:

```bash
/plugin marketplace add alaturqua/mcp-trino-python
/plugin install trino@mcp-trino-python
```

Or add the server directly:

```bash
claude mcp add trino -e TRINO_HOST=localhost -e TRINO_USER=trino -- uvx mcp-trino-python
```

### Claude Desktop

Download `mcp-trino-python.mcpb` from the [latest release](https://github.com/alaturqua/mcp-trino-python/releases/latest)
and double-click it (or drag it into Settings → Extensions). Claude Desktop asks for the Trino connection settings and
installs everything itself; you only need [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.

Or add it manually to `claude_desktop_config.json`:

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

### VS Code / GitHub Copilot

Add to `.vscode/mcp.json` in your workspace (or run **MCP: Add Server**):

```json
{
  "servers": {
    "trino": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-trino-python"],
      "env": { "TRINO_HOST": "localhost", "TRINO_PORT": "8080", "TRINO_USER": "trino" }
    }
  }
}
```

For the GitHub Copilot CLI, put the same entry under `mcpServers` in `~/.copilot/mcp-config.json`.

### Docker

```bash
# stdio (for MCP clients that spawn the container)
docker run -i --rm -e TRINO_HOST=host.docker.internal ghcr.io/alaturqua/mcp-trino-python

# Streamable HTTP on http://localhost:8000/mcp (health check at /health)
docker run --rm -p 8000:8000 -e TRINO_HOST=host.docker.internal ghcr.io/alaturqua/mcp-trino-python --transport http
```

### MCP Registry

The server is listed in the [MCP Registry](https://registry.modelcontextprotocol.io) as
`io.github.alaturqua/mcp-trino-python` ([server.json](server.json)), which MCP clients and marketplaces can install from.

## Configuration

| Variable          | Description                                                       | Default   |
| ----------------- | ----------------------------------------------------------------- | --------- |
| TRINO_HOST        | Trino server hostname                                             | localhost |
| TRINO_PORT        | Trino server port                                                 | 8080      |
| TRINO_USER        | Trino username                                                    | trino     |
| TRINO_PASSWORD    | Password; enables basic auth (use with https)                     | unset     |
| TRINO_HTTP_SCHEME | `http` or `https`                                                 | http      |
| TRINO_CATALOG     | Default catalog, used when a tool call omits it                   | unset     |
| TRINO_SCHEMA      | Default schema, used when a tool call omits it                    | unset     |
| TRINO_READ_ONLY   | `true`: hide maintenance tools and allow only read statements     | false     |
| MCP_TRANSPORT     | `stdio`, `http` or `sse` (legacy); same as `--transport`          | stdio     |
| MCP_HOST          | HTTP bind host; same as `--host`                                  | 127.0.0.1 |
| MCP_PORT          | HTTP port; same as `--port`                                       | 8000      |

Variables can also come from a `.env` file in the working directory; real environment variables take precedence.

Read-only mode checks the statement's first keyword (`SELECT`, `WITH`, `SHOW`, `DESCRIBE`, `EXPLAIN`, `VALUES`).
It is a guard rail, not a security boundary: for hard guarantees, connect with a Trino user that only has read access.

## Development

```bash
git clone https://github.com/alaturqua/mcp-trino-python.git
cd mcp-trino-python
uv sync

docker compose up -d --wait trino   # Trino with TPC-H / TPC-DS sample data on localhost:8080
uv run pytest                       # tests run against that Trino
uv run ruff check
uv run mcp-trino --transport http   # or try it with: npx @modelcontextprotocol/inspector
```

`docker compose up mcp-trino-http` runs Trino plus the server on http://localhost:8000/mcp.

### Releasing

Bump `version` in `pyproject.toml`, then publish a GitHub release tagged `v<version>`. The `Publish` workflow pushes
the package to PyPI, the image to ghcr.io, and `server.json` to the MCP Registry (GitHub OIDC, no secret needed).
It also attaches the Claude Desktop extension (`mcp-trino-python.mcpb`) to the release; build it locally with
`sh mcpb/pack.sh` (needs `npm install -g @anthropic-ai/mcpb`). Bump `version` in `.claude-plugin/plugin.json` too so
Claude Code picks up the update.

## Tools

All `catalog` / `schema_name` parameters are optional when `TRINO_CATALOG` / `TRINO_SCHEMA` are set. Maintenance tools are hidden in read-only mode.

### Query and Exploration Tools

- **show_catalogs**

  - List all available catalogs
  - No parameters required

- **show_schemas**

  - List all schemas in a catalog
  - Parameters:
    - `catalog`: Catalog name (string, optional)

- **show_tables**

  - List all tables in a schema
  - Parameters:
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **describe_table**

  - Show detailed table structure and column information
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **execute_query**

  - Execute a SQL query and return formatted results
  - Parameters:
    - `query`: SQL query to execute (string, required)

- **show_catalog_tree**

  - Show a hierarchical tree view of catalogs, schemas, and tables
  - Returns a formatted tree structure with visual indicators
  - No parameters required

- **show_create_table**

  - Show the CREATE TABLE statement for a table
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **show_create_view**

  - Show the CREATE VIEW statement for a view
  - Parameters:
    - `view`: View name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **show_stats**
  - Show statistics for a table
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

### Iceberg Table Maintenance

- **optimize**

  - Optimize an Iceberg table by compacting small files
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **optimize_manifests**

  - Optimize manifest files for an Iceberg table
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **expire_snapshots**
  - Remove old snapshots from an Iceberg table
  - Parameters:
    - `table`: Table name (string, required)
    - `retention_threshold`: Age threshold (e.g., "7d") (string, optional)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

### Iceberg Metadata Inspection

- **show_table_properties**

  - Show Iceberg table properties
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **show_table_history**

  - Show Iceberg table history/changelog
  - Contains snapshot timing, lineage, and ancestry information
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **show_metadata_log_entries**

  - Show Iceberg table metadata log entries
  - Contains metadata file locations and sequence information
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **show_snapshots**

  - Show Iceberg table snapshots
  - Contains snapshot details including operations and manifest files
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **show_manifests**

  - Show Iceberg table manifests for current or all snapshots
  - Contains manifest file details and data file statistics
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)
    - `all_snapshots`: Include all snapshots (boolean, optional)

- **show_partitions**

  - Show Iceberg table partitions
  - Contains partition statistics and file counts
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **show_files**

  - Show Iceberg table data files in current snapshot
  - Contains detailed file metadata and column statistics
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

- **show_entries**

  - Show Iceberg table manifest entries for current or all snapshots
  - Contains entry status and detailed file metrics
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)
    - `all_snapshots`: Include all snapshots (boolean, optional)

- **show_refs**

  - Show Iceberg table references (branches and tags)
  - Contains reference configuration and snapshot mapping
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema_name`: Schema name (string, optional)

### Query History

- **show_query_history**
  - Get the history of executed queries
  - Parameters:
    - `limit`: Maximum number of queries to return (number, optional)

## License

This project is licensed under the Apache 2.0 License. Please refer to the LICENSE file for the full terms.
