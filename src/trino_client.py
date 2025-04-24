"""Client for interacting with Trino server.

This module provides a client for executing queries and managing operations on Trino,
including specific support for Iceberg table operations.
"""

import json

import trino

from config import TrinoConfig


class TrinoError(Exception):
    """Base class for Trino-related errors."""

    def __init__(self, message: str):
        """Initialize with error message."""
        self.message = message
        super().__init__(self.message)


class CatalogSchemaError(TrinoError):
    """Error raised when catalog or schema information is missing."""

    def __init__(self):
        super().__init__("Both catalog and schema must be specified")


class TrinoClient:
    """A client for interacting with Trino server.

    This class provides methods to execute queries and perform administrative operations
    on a Trino server, with special support for Iceberg table operations.

    Attributes:
        config (TrinoConfig): Configuration object containing Trino connection settings.
        client (trino.dbapi.Connection): Active connection to the Trino server.
    """

    def __init__(self, config: TrinoConfig):
        """Initialize the Trino client.

        Args:
            config (TrinoConfig): Configuration object containing Trino connection settings.
        """
        self.config = config
        self.client = self._create_client()

    def _create_client(self) -> trino.dbapi.Connection:
        """Create a new Trino DB API connection.

        Returns:
            trino.dbapi.Connection: A new connection to the Trino server.
        """
        return trino.dbapi.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            catalog=self.config.catalog,
            schema=self.config.schema,
            http_scheme=self.config.http_scheme,
            auth=self.config.auth,
            source=self.config.source,
        )

    def execute_query(self, query: str) -> str:
        """Execute a SQL query against Trino and return results as a formatted string.

        Args:
            query (str): The SQL query to execute.
            params (Optional[dict]): Dictionary of query parameters with primitive types.

        Returns:
            str: JSON-formatted string containing query results or success message.
        """
        cur: trino.dbapi.Cursor = self.client.cursor()
        cur.execute(query)
        if cur.description:
            return json.dumps(
                [dict(zip([col[0] for col in cur.description], row, strict=True)) for row in cur.fetchall()],
                default=str,
            )
        return "Query executed successfully (no results to display)"

    def get_query_history(self, limit: int) -> str:
        """Retrieve the history of executed queries.

        Args:
            limit (Optional[int]): Maximum number of queries to return. If None, returns all queries.

        Returns:
            str: JSON-formatted string containing query history.
        """
        query = "SELECT * FROM system.runtime.queries"
        if limit is not None:
            query += f" LIMIT {limit}"
        return self.execute_query(query)

    def list_catalogs(self) -> str:
        """List all available catalogs.

        Returns:
            str: Newline-separated list of catalog names.
        """
        catalogs = [row["Catalog"] for row in json.loads(self.execute_query("SHOW CATALOGS"))]
        return "\n".join(catalogs)

    def list_schemas(self, catalog: str) -> str:
        """List all schemas in a catalog.

        Args:
            catalog: The catalog name. If None, uses configured default.

        Returns:
            Newline-separated list of schema names.

        Raises:
            CatalogSchemaError: If no catalog is specified and none is configured.
        """
        catalog = catalog or self.config.catalog
        if not catalog:
            msg = "Catalog must be specified"
            raise CatalogSchemaError(msg)
        query = f"SHOW SCHEMAS FROM {catalog}"
        schemas = [row["Schema"] for row in json.loads(self.execute_query(query))]
        return "\n".join(schemas)

    def list_tables(self, catalog: str, schema: str) -> str:
        """List all tables in a schema.

        Args:
            catalog: The catalog name. If None, uses configured default.
            schema: The schema name. If None, uses configured default.

        Returns:
            Newline-separated list of table names.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            msg = "Both catalog and schema must be specified"
            raise CatalogSchemaError(msg)
        query = f"SHOW TABLES FROM {catalog}.{schema}"
        tables = [row["Table"] for row in json.loads(self.execute_query(query))]
        return "\n".join(tables)

    def describe_table(self, catalog: str, schema: str, table: str) -> str:
        """Describe the structure of a table.

        Args:
            catalog (str): The catalog name. If None, uses configured default.
            schema (str): The schema name. If None, uses configured default.
            table (str): The name of the table.

        Returns:
            str: JSON-formatted string containing table description.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        query = f"DESCRIBE {catalog}.{schema}.{table}"
        return self.execute_query(query)

    def show_create_table(self, catalog: str, schema: str, table: str) -> str:
        """Show the CREATE TABLE statement for a table.

        Args:
            schema (str): The schema name. If None, uses configured default.
            catalog (str): The catalog name. If None, uses configured default.
            table (str): The name of the table.

        Returns:
            str: The CREATE TABLE statement for the specified table.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        query = f"SHOW CREATE TABLE {catalog}.{schema}.{table}"
        result = json.loads(self.execute_query(query))
        return result[0]["Create Table"] if result else ""

    def show_create_view(
        self,
        catalog: str,
        schema: str,
        view: str,
    ) -> str:
        """Show the CREATE VIEW statement for a view.

        Args:
            catalog (str): The catalog name. If None, uses configured default.
            schema (str): The schema name. If None, uses configured default.
            view (str): The name of the view.

        Returns:
            str: The CREATE VIEW statement for the specified view.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        query = f"SHOW CREATE VIEW {catalog}.{schema}.{view}"
        result = json.loads(self.execute_query(query))
        return result[0]["Create View"] if result else ""

    def show_stats(self, catalog: str, schema: str, table: str) -> str:
        """Show statistics for a table.

        Args:
            catalog (str): The catalog name. If None, uses configured default.
            schema (str): The schema name. If None, uses configured default.
            table (str): The name of the table.

        Returns:
            str: JSON-formatted string containing table statistics.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        query = f"SHOW STATS FOR {catalog}.{schema}.{table}"
        return self.execute_query(query)

    def optimize(self, catalog: str, schema: str, table: str) -> str:
        """Optimize an Iceberg table by compacting small files.

        Args:
            catalog (str): The catalog name. If None, uses configured default.
            schema (str): The schema name. If None, uses configured default.
            table (str): The name of the table to optimize.

        Returns:
            str: Success message indicating the table was optimized.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        query = f"ALTER TABLE {catalog}.{schema}.{table} EXECUTE optimize"
        self.execute_query(query)
        return f"Table {catalog}.{schema}.{table} optimized successfully"

    def optimize_manifests(self, table: str, catalog: str, schema: str) -> str:
        """Optimize manifest files for an Iceberg table.

        This operation reorganizes and compacts the table's manifest files for improved
        performance.

        Args:
            table (str): The name of the table.
            catalog (Optional[str]): The catalog name. If None, uses configured default.
            schema (Optional[str]): The schema name. If None, uses configured default.

        Returns:
            str: Success message indicating the manifests were optimized.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        query = f"ALTER TABLE {catalog}.{schema}.{table} EXECUTE optimize_manifests"
        self.execute_query(query)
        return f"Manifests for table {catalog}.{schema}.{table} optimized successfully"

    def expire_snapshots(
        self,
        catalog: str,
        table: str,
        schema: str,
        retention_threshold: str = "7d",
    ) -> str:
        """Remove old snapshots from an Iceberg table.

        This operation removes snapshots older than the specified retention threshold,
        helping to manage storage and improve performance.

        Args:
            table: The name of the table.
            retention_threshold: Age threshold for snapshot removal (e.g., "7d").
            catalog: The catalog name. If None, uses configured default.
            schema: The schema name. If None, uses configured default.

        Returns:
            Success message indicating snapshots were expired.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            msg = "Both catalog and schema must be specified"
            raise CatalogSchemaError(msg)
        query = (
            f"ALTER TABLE {catalog}.{schema}.{table} "
            f"EXECUTE expire_snapshots(retention_threshold => '{retention_threshold}')"
        )
        self.execute_query(query)
        return f"Snapshots older than {retention_threshold} expired for table {catalog}.{schema}.{table}"

    def show_catalog_tree(self) -> str:
        """Show a hierarchical tree view of all catalogs, schemas, and tables.

        Returns:
            A formatted string showing the catalog > schema > table hierarchy.
        """
        tree = []
        catalogs = [row["Catalog"] for row in json.loads(self.execute_query("SHOW CATALOGS"))]
        for catalog in sorted(catalogs):
            tree.append(f"{catalog}")
            try:
                schemas = [row["Schema"] for row in json.loads(self.execute_query(f"SHOW SCHEMAS FROM {catalog}"))]
                for schema in sorted(schemas):
                    tree.append(f"{schema}")
                    try:
                        tables = [
                            row["Table"]
                            for row in json.loads(self.execute_query(f"SHOW TABLES FROM {catalog}.{schema}"))
                        ]
                        tree.extend(f" {table}" for table in sorted(tables))
                    except (trino.dbapi.TrinoQueryError, KeyError):
                        tree.append(" Unable to list tables")
            except (trino.dbapi.TrinoQueryError, KeyError):
                tree.append("Unable to list schemas")
        return "\n".join(tree) if tree else "No catalogs found"

    def show_table_properties(self, table: str, catalog: str, schema: str) -> str:
        """Show Iceberg table properties.

        Args:
            table: The name of the table
            catalog: Optional catalog name (defaults to configured catalog)
            schema: Optional schema name (defaults to configured schema)

        Returns:
            str: JSON-formatted string containing table properties
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        query = 'SELECT * FROM "{}$properties"'
        table_identifier = f"{catalog}.{schema}.{table}"
        return self.execute_query(query.format(table_identifier))

    def show_table_history(self, table: str, catalog: str, schema: str) -> str:
        """Show Iceberg table history/changelog.

        The history contains:
        - made_current_at: TIMESTAMP(3) WITH TIME ZONE - Time when snapshot became active
        - snapshot_id: BIGINT - Identifier of the snapshot
        - parent_id: BIGINT - Identifier of the parent snapshot
        - is_current_ancestor: BOOLEAN - Whether this snapshot is an ancestor of current

        Args:
            table: The name of the table
            catalog: Optional catalog name (defaults to configured catalog)
            schema: Optional schema name (defaults to configured schema)

        Returns:
            str: JSON-formatted string containing table history
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        table_identifier = f"{catalog}.{schema}.{table}"
        query = 'SELECT * FROM "{}$history"'
        return self.execute_query(query.format(table_identifier))

    def show_metadata_log_entries(self, table: str, catalog: str, schema: str) -> str:
        """Show Iceberg table metadata log entries.

        The metadata log contains:
        - timestamp: TIMESTAMP(3) WITH TIME ZONE - Time when metadata was created
        - file: VARCHAR - Location of the metadata file
        - latest_snapshot_id: BIGINT - ID of latest snapshot when metadata was updated
        - latest_schema_id: INTEGER - ID of latest schema when metadata was updated
        - latest_sequence_number: BIGINT - Data sequence number of metadata file

        Args:
            table: The name of the table
            catalog: Optional catalog name (defaults to configured catalog)
            schema: Optional schema name (defaults to configured schema)

        Returns:
            str: JSON-formatted string containing metadata log entries
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        query = 'SELECT * FROM "{}$metadata_log_entries"'
        table_identifier = f"{catalog}.{schema}.{table}"
        return self.execute_query(query.format(table_identifier))

    def show_snapshots(self, table: str, catalog: str, schema: str) -> str:
        """Show Iceberg table snapshots.

        The snapshots table contains:
        - committed_at: TIMESTAMP(3) WITH TIME ZONE - Time when snapshot became active
        - snapshot_id: BIGINT - Identifier for the snapshot
        - parent_id: BIGINT - Identifier for the parent snapshot
        - operation: VARCHAR - Type of operation (append/replace/overwrite/delete)
        - manifest_list: VARCHAR - List of Avro manifest files
        - summary: map(VARCHAR, VARCHAR) - Summary of changes from previous snapshot

        Args:
            table: The name of the table
            catalog: Optional catalog name (defaults to configured catalog)
            schema: Optional schema name (defaults to configured schema)

        Returns:
            str: JSON-formatted string containing table snapshots
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        table_identifier = f"{catalog}.{schema}.{table}$snapshots"
        query = 'SELECT * FROM "{}"'
        return self.execute_query(query.format(table_identifier))

    def show_manifests(self, table: str, catalog: str, schema: str, all_snapshots: bool = False) -> str:
        """Show Iceberg table manifests for current or all snapshots.

        The manifests table contains:
        - path: VARCHAR - Manifest file location
        - length: BIGINT - Manifest file length
        - partition_spec_id: INTEGER - ID of partition spec used
        - added_snapshot_id: BIGINT - ID of snapshot when manifest was added
        - added_data_files_count: INTEGER - Number of data files with status ADDED
        - added_rows_count: BIGINT - Total rows in ADDED files
        - existing_data_files_count: INTEGER - Number of EXISTING files
        - existing_rows_count: BIGINT - Total rows in EXISTING files
        - deleted_data_files_count: INTEGER - Number of DELETED files
        - deleted_rows_count: BIGINT - Total rows in DELETED files
        - partition_summaries: ARRAY(ROW(...)) - Partition range metadata

        Args:
            table: The name of the table
            catalog: Optional catalog name (defaults to configured catalog)
            schema: Optional schema name (defaults to configured schema)
            all_snapshots: If True, show manifests from all snapshots

        Returns:
            str: JSON-formatted string containing table manifests
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        table_type = "all_manifests" if all_snapshots else "manifests"
        query = 'SELECT * FROM "{}${}"'
        table_identifier = f"{catalog}.{schema}.{table}"
        return self.execute_query(query.format(table_identifier, table_type))

    def show_partitions(self, table: str, catalog: str, schema: str) -> str:
        """Show Iceberg table partitions.

        The partitions table contains:
        - partition: ROW(...) - Mapping of partition column names to values
        - record_count: BIGINT - Number of records in partition
        - file_count: BIGINT - Number of files in partition
        - total_size: BIGINT - Total size of files in partition
        - data: ROW(...) - Partition range metadata with min/max values and null/nan counts

        Args:
            table: The name of the table
            catalog: Optional catalog name (defaults to configured catalog)
            schema: Optional schema name (defaults to configured schema)

        Returns:
            str: JSON-formatted string containing table partitions
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        table_identifier = f"{catalog}.{schema}.{table}$partitions"
        query = 'SELECT * FROM "{}"'
        return self.execute_query(query.format(table_identifier))

    def show_files(self, table: str, catalog: str, schema: str) -> str:
        """Show Iceberg table data files in current snapshot.

        The files table contains:
        - content: INTEGER - Type of content (0=DATA, 1=POSITION_DELETES, 2=EQUALITY_DELETES)
        - file_path: VARCHAR - Data file location
        - file_format: VARCHAR - Format of the data file
        - record_count: BIGINT - Number of records in file
        - file_size_in_bytes: BIGINT - File size
        - column_sizes: map(INTEGER, BIGINT) - Column ID to size mapping
        - value_counts: map(INTEGER, BIGINT) - Column ID to value count mapping
        - null_value_counts: map(INTEGER, BIGINT) - Column ID to null count mapping
        - nan_value_counts: map(INTEGER, BIGINT) - Column ID to NaN count mapping
        - lower_bounds: map(INTEGER, VARCHAR) - Column ID to lower bound mapping
        - upper_bounds: map(INTEGER, VARCHAR) - Column ID to upper bound mapping
        - key_metadata: VARBINARY - Encryption key metadata
        - split_offsets: array(BIGINT) - Recommended split locations
        - equality_ids: array(INTEGER) - Field IDs for equality deletes

        Args:
            table: The name of the table
            catalog: Optional catalog name (defaults to configured catalog)
            schema: Optional schema name (defaults to configured schema)

        Returns:
            str: JSON-formatted string containing table files info
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        table_identifier = f"{catalog}.{schema}.{table}$files"
        query = 'SELECT * FROM "{}"'
        return self.execute_query(query.format(table_identifier))

    def show_entries(self, table: str, catalog: str, schema: str, all_snapshots: bool = False) -> str:
        """Show Iceberg table manifest entries for current or all snapshots.

        The entries table contains:
        - status: INTEGER - Status of entry (0=EXISTING, 1=ADDED, 2=DELETED)
        - snapshot_id: BIGINT - ID of the snapshot
        - sequence_number: BIGINT - Data sequence number
        - file_sequence_number: BIGINT - File sequence number
        - data_file: ROW(...) - File metadata including path, format, size etc
        - readable_metrics: JSON - Human-readable file metrics

        Args:
            table: The name of the table
            catalog: Optional catalog name (defaults to configured catalog)
            schema: Optional schema name (defaults to configured schema)
            all_snapshots: If True, show entries from all snapshots

        Returns:
            str: JSON-formatted string containing manifest entries
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        table_name = f"{catalog}.{schema}.{table}${'all_' if all_snapshots else ''}entries"
        query = 'SELECT * FROM "{}"'
        return self.execute_query(query.format(table_name))

    def show_refs(self, table: str, catalog: str, schema: str) -> str:
        """Show Iceberg table references (branches and tags).

        The refs table contains:
        - name: VARCHAR - Name of the reference
        - type: VARCHAR - Type of reference (BRANCH or TAG)
        - snapshot_id: BIGINT - ID of referenced snapshot
        - max_reference_age_in_ms: BIGINT - Max age before reference expiry
        - min_snapshots_to_keep: INTEGER - Min snapshots to keep (branches only)
        - max_snapshot_age_in_ms: BIGINT - Max snapshot age in branch

        Args:
            table: The name of the table
            catalog: Optional catalog name (defaults to configured catalog)
            schema: Optional schema name (defaults to configured schema)

        Returns:
            str: JSON-formatted string containing table references
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        table_identifier = f"{catalog}.{schema}.{table}$refs"
        query = 'SELECT * FROM "{}"'
        return self.execute_query(query.format(table_identifier))
