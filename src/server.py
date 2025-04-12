"""Model Context Protocol server for Trino.

This module provides a Model Context Protocol (MCP) server that exposes Trino
functionality through resources and tools, with special support for Iceberg tables.
"""

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

from config import load_config
from trino_client import TrinoClient

# Initialize the MCP server and Trino client
config = load_config()
client = TrinoClient(config)
mcp = FastMCP("Trino Explorer", dependencies=["trino", "python-dotenv", "loguru"])


# Resources
@mcp.resource(
    "catalog://main",
    name="list_catalogs",
    description="List all available Trino catalogs",
)
def list_catalogs() -> str:
    """List all available Trino catalogs."""
    return client.list_catalogs()


@mcp.resource(
    "schema://{catalog}",
    name="list_schemas",
    description="List all schemas in the specified catalog",
)
def list_schemas(catalog: str) -> str:
    """List all schemas in a catalog."""
    return client.list_schemas(catalog)


@mcp.resource(
    "table://{catalog}/{schema}",
    name="list_tables",
    description="List all tables in the specified schema",
)
def list_tables(catalog: str, schema: str) -> str:
    """List all tables in a schema."""
    return client.list_tables(catalog, schema)


# Tools
@mcp.tool(description="Show the CREATE TABLE statement for a specific table")
def show_create_table(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Show the CREATE TABLE statement for a table.

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: The CREATE TABLE statement
    """
    return client.show_create_table(table, catalog, schema)


@mcp.tool(description="Show the CREATE VIEW statement for a specific view")
def show_create_view(view: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Show the CREATE VIEW statement for a view.

    Args:
        view: The name of the view
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: The CREATE VIEW statement
    """
    return client.show_create_view(view, catalog, schema)


@mcp.tool(description="Execute a SQL query and return results in a readable format")
def execute_query(query: str) -> str:
    """Execute a SQL query and return formatted results.

    Args:
        query: The SQL query to execute

    Returns:
        str: Query results formatted as a JSON string
    """
    return client.execute_query(query)


@mcp.tool(description="Optimize an Iceberg table's data files")
def optimize(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Optimize an Iceberg table by compacting small files.

    Args:
        table: The name of the table to optimize
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: Confirmation message
    """
    return client.optimize(table, catalog, schema)


@mcp.tool(description="Optimize manifest files for an Iceberg table")
def optimize_manifests(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Optimize manifest files for an Iceberg table.

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: Confirmation message
    """
    return client.optimize_manifests(table, catalog, schema)


@mcp.tool(description="Remove old snapshots from an Iceberg table")
def expire_snapshots(
    table: str,
    retention_threshold: str = "7d",
    catalog: str | None = None,
    schema: str | None = None,
) -> str:
    """Remove old snapshots from an Iceberg table.

    Args:
        table: The name of the table
        retention_threshold: Age threshold for snapshot removal (e.g., "7d", "30d")
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: Confirmation message
    """
    return client.expire_snapshots(table, retention_threshold, catalog, schema)


@mcp.tool(description="Show statistics for a table")
def show_stats(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Show statistics for a table.

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: Table statistics in JSON format
    """
    return client.show_stats(table, catalog, schema)


@mcp.tool(name="show_query_history", description="Get the history of executed queries")
def show_query_history(limit: int | None = None) -> str:
    """Get the history of executed queries.

    Args:
        limit: Optional maximum number of history entries to return.
            If None, returns all entries.

    Returns:
        str: JSON-formatted string containing query history.
    """
    return client.get_query_history(limit)


@mcp.tool(description="Show a hierarchical tree view of catalogs, schemas, and tables")
def show_catalog_tree() -> str:
    """Get a hierarchical tree view showing the full structure of catalogs, schemas, and tables.

    Returns:
        str: A formatted string showing the catalog > schema > table hierarchy with visual indicators
    """
    return client.show_catalog_tree()


# Prompts
@mcp.prompt()
def explore_data(catalog: str | None = None, schema: str | None = None) -> list[base.Message]:
    """Interactive prompt to explore Trino data."""
    messages = [
        base.SystemMessage(
            "I'll help you explore data in Trino. I can show you available catalogs, "
            "schemas, and tables, and help you query the data."
        )
    ]

    if catalog and schema:
        messages.append(
            base.UserMessage(
                f"Show me what tables are available in the {catalog}.{schema} schema and help me query them."
            )
        )
    elif catalog:
        messages.append(base.UserMessage(f"Show me what schemas are available in the {catalog} catalog."))
    else:
        messages.append(base.UserMessage("Show me what catalogs are available."))

    return messages


@mcp.prompt()
def maintain_iceberg(table: str, catalog: str | None = None, schema: str | None = None) -> list[base.Message]:
    """Interactive prompt for Iceberg table maintenance."""
    return [
        base.SystemMessage(
            "I'll help you maintain an Iceberg table. I can help with optimization, "
            "cleaning up snapshots and orphan files, and viewing table metadata."
        ),
        base.UserMessage(
            f"What maintenance operations should we perform on the Iceberg table "
            f"{catalog + '.' if catalog else ''}{schema + '.' if schema else ''}{table}?"
        ),
    ]


if __name__ == "__main__":
    from loguru import logger

    logger.info("Starting Trino MCP server...")
    mcp.run()
