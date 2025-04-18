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
    name="show_catalogs",
    description="List all available Trino catalogs",
)
def show_catalogs() -> str:
    """List all available Trino catalogs."""
    return client.show_catalogs()


@mcp.resource(
    "schema://{catalog}",
    name="show_schemas",
    description="List all schemas in the specified catalog",
)
def show_schemas(catalog: str) -> str:
    """List all schemas in a catalog."""
    return client.show_schemas(catalog)


@mcp.resource(
    "table://{catalog}/{schema}",
    name="show_tables",
    description="List all tables in the specified schema",
)
def show_tables(catalog: str, schema: str) -> str:
    """List all tables in a schema."""
    return client.show_tables(catalog, schema)


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


@mcp.tool(description="Show Iceberg table properties")
def show_table_properties(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Show Iceberg table properties.

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: JSON-formatted table properties
    """
    return client.show_table_properties(table, catalog, schema)


@mcp.tool(description="Show Iceberg table history/changelog")
def show_table_history(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Show Iceberg table history/changelog.

    The history contains:
    - made_current_at: When snapshot became active
    - snapshot_id: Identifier of the snapshot
    - parent_id: Identifier of the parent snapshot
    - is_current_ancestor: Whether snapshot is an ancestor of current

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: JSON-formatted table history
    """
    return client.show_table_history(table, catalog, schema)


@mcp.tool(description="Show Iceberg table metadata log entries")
def show_metadata_log_entries(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Show Iceberg table metadata log entries.

    The metadata log contains:
    - timestamp: When metadata was created
    - file: Location of the metadata file
    - latest_snapshot_id: ID of latest snapshot when metadata was updated
    - latest_schema_id: ID of latest schema when metadata was updated
    - latest_sequence_number: Data sequence number of metadata file

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: JSON-formatted metadata log entries
    """
    return client.show_metadata_log_entries(table, catalog, schema)


@mcp.tool(description="Show Iceberg table snapshots")
def show_snapshots(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Show Iceberg table snapshots.

    The snapshots table contains:
    - committed_at: When snapshot became active
    - snapshot_id: Identifier for the snapshot
    - parent_id: Identifier for the parent snapshot
    - operation: Type of operation (append/replace/overwrite/delete)
    - manifest_list: List of Avro manifest files
    - summary: Summary of changes from previous snapshot

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: JSON-formatted table snapshots
    """
    return client.show_snapshots(table, catalog, schema)


@mcp.tool(description="Show Iceberg table manifests")
def show_manifests(
    table: str, catalog: str | None = None, schema: str | None = None, all_snapshots: bool = False
) -> str:
    """Show Iceberg table manifests for current or all snapshots.

    The manifests table contains:
    - path: Manifest file location
    - length: Manifest file length
    - partition_spec_id: ID of partition spec used
    - added_snapshot_id: ID of snapshot when manifest was added
    - added_data_files_count: Number of data files with status ADDED
    - added_rows_count: Total rows in ADDED files
    - existing_data_files_count: Number of EXISTING files
    - existing_rows_count: Total rows in EXISTING files
    - deleted_data_files_count: Number of DELETED files
    - deleted_rows_count: Total rows in DELETED files
    - partition_summaries: Partition range metadata

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)
        all_snapshots: If True, show manifests from all snapshots

    Returns:
        str: JSON-formatted table manifests
    """
    return client.show_manifests(table, catalog, schema, all_snapshots)


@mcp.tool(description="Show Iceberg table partitions")
def show_partitions(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Show Iceberg table partitions.

    The partitions table contains:
    - partition: Mapping of partition column names to values
    - record_count: Number of records in partition
    - file_count: Number of files in partition
    - total_size: Total size of files in partition
    - data: Partition range metadata with min/max values and null/nan counts

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: JSON-formatted table partitions
    """
    return client.show_partitions(table, catalog, schema)


@mcp.tool(description="Show Iceberg table data files")
def show_files(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Show Iceberg table data files in current snapshot.

    The files table contains:
    - content: Type of content (0=DATA, 1=POSITION_DELETES, 2=EQUALITY_DELETES)
    - file_path: Data file location
    - file_format: Format of the data file
    - record_count: Number of records in file
    - file_size_in_bytes: File size
    - column_sizes: Column ID to size mapping
    - value_counts: Column ID to value count mapping
    - null_value_counts: Column ID to null count mapping
    - nan_value_counts: Column ID to NaN count mapping
    - lower_bounds: Column ID to lower bound mapping
    - upper_bounds: Column ID to upper bound mapping
    - key_metadata: Encryption key metadata
    - split_offsets: Recommended split locations
    - equality_ids: Field IDs for equality deletes

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: JSON-formatted table files info
    """
    return client.show_files(table, catalog, schema)


@mcp.tool(description="Show Iceberg table manifest entries")
def show_entries(table: str, catalog: str | None = None, schema: str | None = None, all_snapshots: bool = False) -> str:
    """Show Iceberg table manifest entries for current or all snapshots.

    The entries table contains:
    - status: Status of entry (0=EXISTING, 1=ADDED, 2=DELETED)
    - snapshot_id: ID of the snapshot
    - sequence_number: Data sequence number
    - file_sequence_number: File sequence number
    - data_file: File metadata including path, format, size etc
    - readable_metrics: Human-readable file metrics

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)
        all_snapshots: If True, show entries from all snapshots

    Returns:
        str: JSON-formatted manifest entries
    """
    return client.show_entries(table, catalog, schema, all_snapshots)


@mcp.tool(description="Show Iceberg table references (branches and tags)")
def show_refs(table: str, catalog: str | None = None, schema: str | None = None) -> str:
    """Show Iceberg table references (branches and tags).

    The refs table contains:
    - name: Name of the reference
    - type: Type of reference (BRANCH or TAG)
    - snapshot_id: ID of referenced snapshot
    - max_reference_age_in_ms: Max age before reference expiry
    - min_snapshots_to_keep: Min snapshots to keep (branches only)
    - max_snapshot_age_in_ms: Max snapshot age in branch

    Args:
        table: The name of the table
        catalog: Optional catalog name (defaults to configured catalog)
        schema: Optional schema name (defaults to configured schema)

    Returns:
        str: JSON-formatted table references
    """
    return client.show_refs(table, catalog, schema)


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
