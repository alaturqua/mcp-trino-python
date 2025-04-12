# MCP Trino Server

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
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
2. Python 3.11 or higher
3. Docker (optional, for containerized deployment)

## Installation

### Running Trino Locally

The easiest way to get started is to use the included Docker Compose configuration to run Trino locally:

```bash
docker-compose up -d
```

This will start a Trino server on `localhost:8080`. You can now proceed with configuring the MCP server.

### Usage with VS Code

For quick installation, you can add the following configuration to your VS Code settings. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open User Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.

> Note that the `mcp` key is not needed in the `.vscode/mcp.json` file.

```json
{
  "mcp": {
    "servers": {
      "trino": {
        "command": "docker",
        "args": ["run", "--rm", "ghcr.io/alaturqua/mcp-trino-python:latest"],
        "env": {
          "TRINO_HOST": "${input:trino_host}",
          "TRINO_PORT": "${input:trino_port}",
          "TRINO_USER": "${input:trino_user}"
        }
      }
    }
  }
}
```

### Usage with Claude Desktop

Add the following configuration to your Claude Desktop settings:

```json
{
  "mcpServers": {
    "trino": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "TRINO_HOST": "your-trino-host",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino"
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
| TRINO_AUTH        | Authentication method    | None      |

## Resources

The server provides the following MCP resources:

### Catalog and Schema Navigation

- **catalog://main** (`list_catalogs`)

  - Lists all available Trino catalogs
  - No parameters required

- **schema://{catalog}** (`list_schemas`)

  - Lists all schemas in the specified catalog
  - Parameters:
    - `catalog`: Catalog name (string, required)

- **table://{catalog}/{schema}** (`list_tables`)
  - Lists all tables in the specified schema
  - Parameters:
    - `catalog`: Catalog name (string, required)
    - `schema`: Schema name (string, required)

## Tools

### Query and Exploration Tools

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

### Query History

- **show_query_history**
  - Get the history of executed queries
  - Parameters:
    - `limit`: Maximum number of queries to return (number, optional)

## License

This project is licensed under the Apache 2.0 License. Please refer to the LICENSE file for the full terms.
