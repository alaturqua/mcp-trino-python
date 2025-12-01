# MCP Trino Server

[![smithery badge](https://smithery.ai/badge/@alaturqua/mcp-trino-python)](https://smithery.ai/server/@alaturqua/mcp-trino-python)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![VS Code](https://img.shields.io/badge/vscode-available-007ACC.svg?style=flat-square&logo=visual-studio-code&logoColor=white)](https://code.visualstudio.com/)
[![Docker](https://img.shields.io/badge/docker-available-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://github.com/alaturqua/mcp-trino-python/pkgs/container/mcp-trino-python)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square)](https://opensource.org/licenses/Apache-2.0)

The MCP Trino Server is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)
server that provides seamless integration with Trino and Iceberg, enabling advanced
data exploration, querying, and table maintenance capabilities through a standard interface.

## Use Cases

- Interactive data exploration and analysis in Trino
- Automated Iceberg table maintenance and optimization
- Building AI-powered tools that interact with Trino databases
- Executing and managing SQL queries with proper result formatting

## Prerequisites

1. A running Trino server (or Docker Compose for local development)
2. Python 3.12 or higher
3. Docker (optional, for containerized deployment)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/alaturqua/mcp-trino-python.git
cd mcp-trino-python
```

### 2. Create Environment File

Create a `.env` file in the root directory:

```bash
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_USER=trino
TRINO_CATALOG=tpch
TRINO_SCHEMA=tiny
```

### 3. Run Trino Locally (Optional)

```bash
docker-compose up -d trino
```

This starts a Trino server on `localhost:8080` with sample TPC-H and TPC-DS data.

## Installation

### Installing via Smithery

To install MCP Trino Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@alaturqua/mcp-trino-python):

```bash
npx -y @smithery/cli install @alaturqua/mcp-trino-python --client claude
```

### Using uv (Recommended)

```bash
uv sync
uv run src/server.py
```

### Using pip

```bash
pip install -e .
python src/server.py
```

## Transport Modes

The server supports three transport modes:

| Transport | Description | Use Case |
|-----------|-------------|----------|
| `stdio` | Standard I/O (default) | VS Code, Claude Desktop, local MCP clients |
| `streamable-http` | HTTP with streaming | Remote access, web clients, Docker |
| `sse` | Server-Sent Events | Legacy HTTP transport |

### Running with Different Transports

```bash
# stdio (default) - for VS Code and Claude Desktop
python src/server.py

# Streamable HTTP - for remote/web access
python src/server.py --transport streamable-http --host 0.0.0.0 --port 8000

# SSE - legacy HTTP transport
python src/server.py --transport sse --host 0.0.0.0 --port 8000
```

## Usage with VS Code

Add to your VS Code settings (`Ctrl+Shift+P` → `Preferences: Open User Settings (JSON)`):

```json
{
  "mcp": {
    "servers": {
      "mcp-trino-python": {
        "command": "uv",
        "args": [
          "run",
          "--with", "mcp[cli]",
          "--with", "trino",
          "--with", "loguru",
          "mcp", "run",
          "/path/to/mcp-trino-python/src/server.py"
        ],
        "envFile": "/path/to/mcp-trino-python/.env"
      }
    }
  }
}
```

Or add to `.vscode/mcp.json` in your workspace (without the `mcp` wrapper key).

## Usage with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "trino": {
      "command": "python",
      "args": ["./src/server.py"],
      "env": {
        "TRINO_HOST": "your-trino-host",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino"
      }
    }
  }
}
```

## Docker Usage

### Build the Image

```bash
docker build -t mcp-trino-python .
```

### Run with stdio (for VS Code)

```bash
docker run -i --rm \
  -e TRINO_HOST=host.docker.internal \
  -e TRINO_PORT=8080 \
  -e TRINO_USER=trino \
  mcp-trino-python
```

### Run with Streamable HTTP

```bash
docker run -p 8000:8000 \
  -e TRINO_HOST=host.docker.internal \
  -e TRINO_PORT=8080 \
  mcp-trino-python \
  --transport streamable-http --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
# Start Trino + MCP server with Streamable HTTP
docker-compose up -d

# Start with SSE transport
docker-compose --profile sse up -d

# Run stdio for testing
docker-compose --profile stdio run --rm mcp-trino-stdio
```

### VS Code with Docker

```json
{
  "mcp": {
    "servers": {
      "mcp-trino-python": {
        "command": "docker",
        "args": [
          "run", "-i", "--rm",
          "--network", "mcp-trino-python_trino-network",
          "-e", "TRINO_HOST=trino",
          "-e", "TRINO_PORT=8080",
          "-e", "TRINO_USER=trino",
          "mcp-trino-python"
        ]
      }
    }
  }
}
```

## Configuration

### Environment Variables

| Variable          | Description              | Default   |
| ----------------- | ------------------------ | --------- |
| TRINO_HOST        | Trino server hostname    | localhost |
| TRINO_PORT        | Trino server port        | 8080      |
| TRINO_USER        | Trino username           | trino     |
| TRINO_CATALOG     | Default catalog          | None      |
| TRINO_SCHEMA      | Default schema           | None      |
| TRINO_HTTP_SCHEME | HTTP scheme (http/https) | http      |
| TRINO_PASSWORD    | Trino password           | None      |

## Tools

### Query and Exploration Tools

- **show_catalogs**

  - List all available catalogs
  - No parameters required

- **show_schemas**

  - List all schemas in a catalog
  - Parameters:
    - `catalog`: Catalog name (string, required)

- **show_tables**

  - List all tables in a schema
  - Parameters:
    - `catalog`: Catalog name (string, required)
    - `schema`: Schema name (string, required)

- **describe_table**

  - Show detailed table structure and column information
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

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
    - `schema`: Schema name (string, optional)

- **show_create_view**

  - Show the CREATE VIEW statement for a view
  - Parameters:
    - `view`: View name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

- **show_stats**
  - Show statistics for a table
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

### Iceberg Table Maintenance

- **optimize**

  - Optimize an Iceberg table by compacting small files
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

- **optimize_manifests**

  - Optimize manifest files for an Iceberg table
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

- **expire_snapshots**
  - Remove old snapshots from an Iceberg table
  - Parameters:
    - `table`: Table name (string, required)
    - `retention_threshold`: Age threshold (e.g., "7d") (string, optional)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

### Iceberg Metadata Inspection

- **show_table_properties**

  - Show Iceberg table properties
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

- **show_table_history**

  - Show Iceberg table history/changelog
  - Contains snapshot timing, lineage, and ancestry information
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

- **show_metadata_log_entries**

  - Show Iceberg table metadata log entries
  - Contains metadata file locations and sequence information
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

- **show_snapshots**

  - Show Iceberg table snapshots
  - Contains snapshot details including operations and manifest files
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

- **show_manifests**

  - Show Iceberg table manifests for current or all snapshots
  - Contains manifest file details and data file statistics
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)
    - `all_snapshots`: Include all snapshots (boolean, optional)

- **show_partitions**

  - Show Iceberg table partitions
  - Contains partition statistics and file counts
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

- **show_files**

  - Show Iceberg table data files in current snapshot
  - Contains detailed file metadata and column statistics
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

- **show_entries**

  - Show Iceberg table manifest entries for current or all snapshots
  - Contains entry status and detailed file metrics
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)
    - `all_snapshots`: Include all snapshots (boolean, optional)

- **show_refs**

  - Show Iceberg table references (branches and tags)
  - Contains reference configuration and snapshot mapping
  - Parameters:
    - `table`: Table name (string, required)
    - `catalog`: Catalog name (string, optional)
    - `schema`: Schema name (string, optional)

### Query History

- **show_query_history**
  - Get the history of executed queries
  - Parameters:
    - `limit`: Maximum number of queries to return (number, optional)

## License

This project is licensed under the Apache 2.0 License. Please refer to the LICENSE file for the full terms.
