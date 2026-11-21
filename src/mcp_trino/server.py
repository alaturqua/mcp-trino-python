"""Model Context Protocol server for Trino, with Iceberg table support."""

import argparse
import os
from importlib.metadata import version
from typing import Annotated

import trino
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.prompts import Message
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools import ToolResult
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import load_config
from .trino_client import TrinoClient, TrinoError


class TrinoErrorMiddleware(Middleware):
    """Turn expected query errors into ToolErrors: the model gets the message, logs skip the traceback."""

    async def on_call_tool(self, context: MiddlewareContext, call_next: CallNext) -> ToolResult:
        try:
            return await call_next(context)
        except TrinoError as e:
            raise ToolError(str(e)) from e
        except trino.exceptions.TrinoUserError as e:
            raise ToolError(f"{e.error_name}: {e.message}") from e


config = load_config()
client = TrinoClient(config)

mcp = FastMCP(
    name="Trino Explorer",
    instructions=(
        "Access to a Trino query engine: browse catalogs, schemas and tables, run SQL, "
        "and inspect or maintain Iceberg tables. Use show_catalogs / show_schemas / show_tables "
        "to discover data before writing queries."
    ),
    version=version("mcp-trino-python"),
    website_url="https://github.com/alaturqua/mcp-trino-python",
    middleware=[TrinoErrorMiddleware()],
)

READ = {"read_only_hint": True, "open_world_hint": True}
WRITE = {"read_only_hint": False, "destructive_hint": True, "open_world_hint": True}

Catalog = Annotated[str | None, Field(description="Catalog name (defaults to TRINO_CATALOG)")]
Schema = Annotated[str | None, Field(description="Schema name (defaults to TRINO_SCHEMA)")]
Table = Annotated[str, Field(description="Table name")]
AllSnapshots = Annotated[bool, Field(description="Include all snapshots instead of only the current one")]


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    """Liveness probe for HTTP deployments."""
    return JSONResponse({"status": "ok"})


# Discovery tools
@mcp.tool(annotations=READ)
def show_catalogs() -> str:
    """List all available catalogs."""
    return client.list_catalogs()


@mcp.tool(annotations=READ)
def show_schemas(catalog: Catalog = None) -> str:
    """List all schemas in a catalog."""
    return client.list_schemas(catalog)


@mcp.tool(annotations=READ)
def show_tables(catalog: Catalog = None, schema_name: Schema = None) -> str:
    """List all tables in a schema."""
    return client.list_tables(catalog, schema_name)


@mcp.tool(annotations=READ)
def describe_table(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Describe a table's columns and types (JSON)."""
    return client.describe_table(catalog, schema_name, table)


@mcp.tool(annotations=READ)
def show_create_table(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Show the CREATE TABLE statement for a table."""
    return client.show_create_table(catalog, schema_name, table)


@mcp.tool(annotations=READ)
def show_create_view(
    view: Annotated[str, Field(description="View name")], catalog: Catalog = None, schema_name: Schema = None
) -> str:
    """Show the CREATE VIEW statement for a view."""
    return client.show_create_view(catalog, schema_name, view)


@mcp.tool(annotations=READ)
def show_stats(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Show column statistics for a table (JSON)."""
    return client.show_stats(catalog, schema_name, table)


@mcp.tool(annotations=READ)
def show_catalog_tree() -> str:
    """Show a hierarchical tree of all catalogs, schemas and tables. Can be slow on large installations."""
    return client.show_catalog_tree()


@mcp.tool(annotations=READ)
def show_query_history(
    limit: Annotated[int | None, Field(description="Maximum number of entries to return", ge=1)] = None,
) -> str:
    """Show recently executed queries from system.runtime.queries, newest first (JSON)."""
    return client.get_query_history(limit)


# Query tool: may write unless TRINO_READ_ONLY is set, so it is not marked read-only.
@mcp.tool(annotations={"read_only_hint": False, "destructive_hint": True, "open_world_hint": True})
def execute_query(query: Annotated[str, Field(description="The SQL statement to execute")]) -> str:
    """Execute a SQL statement and return the rows as JSON.

    In read-only mode only SELECT, WITH, SHOW, DESCRIBE, EXPLAIN and VALUES statements are allowed.
    """
    return client.execute_query(query)


# Iceberg maintenance tools (hidden in read-only mode)
@mcp.tool(annotations=WRITE, tags={"write"})
def optimize(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Compact small data files of an Iceberg table."""
    return client.optimize(catalog, schema_name, table)


@mcp.tool(annotations=WRITE, tags={"write"})
def optimize_manifests(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Rewrite and compact the manifest files of an Iceberg table."""
    return client.optimize_manifests(catalog, schema_name, table)


@mcp.tool(annotations=WRITE, tags={"write"})
def expire_snapshots(
    table: Table,
    catalog: Catalog = None,
    schema_name: Schema = None,
    retention_threshold: Annotated[str, Field(description="Minimum snapshot age to remove, e.g. '7d' or '12h'")] = "7d",
) -> str:
    """Remove Iceberg snapshots older than the retention threshold."""
    return client.expire_snapshots(catalog, schema_name, table, retention_threshold)


# Iceberg metadata tools
@mcp.tool(annotations=READ)
def show_table_properties(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Show Iceberg table properties (JSON)."""
    return client.show_table_properties(catalog, schema_name, table)


@mcp.tool(annotations=READ)
def show_table_history(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Show Iceberg table history (JSON).

    Columns: made_current_at, snapshot_id, parent_id, is_current_ancestor.
    """
    return client.show_table_history(catalog, schema_name, table)


@mcp.tool(annotations=READ)
def show_metadata_log_entries(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Show Iceberg metadata log entries (JSON).

    Columns: timestamp, file, latest_snapshot_id, latest_schema_id, latest_sequence_number.
    """
    return client.show_metadata_log_entries(catalog, schema_name, table)


@mcp.tool(annotations=READ)
def show_snapshots(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Show Iceberg table snapshots (JSON).

    Columns: committed_at, snapshot_id, parent_id, operation, manifest_list, summary.
    """
    return client.show_snapshots(catalog, schema_name, table)


@mcp.tool(annotations=READ)
def show_manifests(
    table: Table, catalog: Catalog = None, schema_name: Schema = None, all_snapshots: AllSnapshots = False
) -> str:
    """Show Iceberg manifest files (JSON).

    Columns: path, length, partition_spec_id, added_snapshot_id, added/existing/deleted data file and row
    counts, partition_summaries.
    """
    return client.show_manifests(catalog, schema_name, table, all_snapshots)


@mcp.tool(annotations=READ)
def show_partitions(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Show Iceberg table partitions (JSON).

    Columns: partition, record_count, file_count, total_size, data (per-column min/max and null counts).
    """
    return client.show_partitions(catalog, schema_name, table)


@mcp.tool(annotations=READ)
def show_files(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Show Iceberg data files in the current snapshot (JSON).

    Columns include content (0=DATA, 1=POSITION_DELETES, 2=EQUALITY_DELETES), file_path, file_format,
    record_count, file_size_in_bytes, column sizes/counts and lower/upper bounds.
    """
    return client.show_files(catalog, schema_name, table)


@mcp.tool(annotations=READ)
def show_entries(
    table: Table, catalog: Catalog = None, schema_name: Schema = None, all_snapshots: AllSnapshots = False
) -> str:
    """Show Iceberg manifest entries (JSON).

    Columns: status (0=EXISTING, 1=ADDED, 2=DELETED), snapshot_id, sequence_number, file_sequence_number,
    data_file, readable_metrics.
    """
    return client.show_entries(catalog, schema_name, table, all_snapshots)


@mcp.tool(annotations=READ)
def show_refs(table: Table, catalog: Catalog = None, schema_name: Schema = None) -> str:
    """Show Iceberg table references, i.e. branches and tags (JSON)."""
    return client.show_refs(catalog, schema_name, table)


# Prompts
@mcp.prompt(title="Explore Trino Data")
def explore_data(catalog: str | None = None, schema_name: str | None = None) -> list[Message]:
    """Guide a conversation exploring Trino data."""
    if catalog and schema_name:
        ask = f"Show me what tables are available in the {catalog}.{schema_name} schema and help me query them."
    elif catalog:
        ask = f"Show me what schemas are available in the {catalog} catalog."
    else:
        ask = "Show me what catalogs are available."
    return [
        Message(
            "I'll help you explore data in Trino. I can show you available catalogs, "
            "schemas, and tables, and help you query the data.",
            role="assistant",
        ),
        Message(ask),
    ]


@mcp.prompt(title="Maintain Iceberg Table")
def maintain_iceberg(table: str, catalog: str | None = None, schema_name: str | None = None) -> list[Message]:
    """Guide Iceberg table maintenance."""
    name = ".".join(part for part in (catalog, schema_name, table) if part)
    return [
        Message(
            "I'll help you maintain an Iceberg table. I can help with optimization, "
            "cleaning up snapshots, and viewing table metadata.",
            role="assistant",
        ),
        Message(f"What maintenance operations should we perform on the Iceberg table {name}?"),
    ]


if config.read_only:
    mcp.disable(tags={"write"})


def main() -> None:
    """Entry point for the `mcp-trino` command."""
    parser = argparse.ArgumentParser(description="MCP server for Trino")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "streamable-http", "sse"],
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        help="stdio (default, local clients), http (Streamable HTTP, for remote use; endpoint /mcp), "
        "sse (legacy, only for old clients)",
    )
    parser.add_argument("--host", default=os.getenv("MCP_HOST", "127.0.0.1"), help="HTTP bind host")
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", "8000")), help="HTTP port")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(show_banner=False)
    else:
        transport = "http" if args.transport == "streamable-http" else args.transport
        mcp.run(
            transport=transport, show_banner=False, host=args.host, port=args.port, stateless_http=transport == "http"
        )


if __name__ == "__main__":
    main()
