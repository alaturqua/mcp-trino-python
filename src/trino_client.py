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

        Returns:
            str: JSON-formatted string containing query results or success message.
        """
        cur = self.client.cursor()
        cur.execute(query)
        if cur.description:
            return json.dumps(
                [dict(zip([col[0] for col in cur.description], row, strict=True)) for row in cur.fetchall()],
                default=str,
            )
        return "Query executed successfully (no results to display)"

    def get_query_history(self, limit: int | None = None) -> str:
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

    def list_schemas(self, catalog: str | None = None) -> str:
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

    def list_tables(self, catalog: str | None = None, schema: str | None = None) -> str:
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

    def show_create_table(self, table: str, catalog: str | None = None, schema: str | None = None) -> str:
        """Show the CREATE TABLE statement for a table.

        Args:
            table (str): The name of the table.
            catalog (Optional[str]): The catalog name. If None, uses configured default.
            schema (Optional[str]): The schema name. If None, uses configured default.

        Returns:
            str: The CREATE TABLE statement for the specified table.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError()
        query = f"SHOW CREATE TABLE {catalog}.{schema}.{table}"
        result = json.loads(self.execute_query(query))
        return result[0]["Create Table"] if result else ""

    def show_create_view(self, view: str, catalog: str | None = None, schema: str | None = None) -> str:
        """Show the CREATE VIEW statement for a view.

        Args:
            view (str): The name of the view.
            catalog (Optional[str]): The catalog name. If None, uses configured default.
            schema (Optional[str]): The schema name. If None, uses configured default.

        Returns:
            str: The CREATE VIEW statement for the specified view.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError()
        query = f"SHOW CREATE VIEW {catalog}.{schema}.{view}"
        result = json.loads(self.execute_query(query))
        return result[0]["Create View"] if result else ""

    def show_stats(self, table: str, catalog: str | None = None, schema: str | None = None) -> str:
        """Show statistics for a table.

        Args:
            table (str): The name of the table.
            catalog (Optional[str]): The catalog name. If None, uses configured default.
            schema (Optional[str]): The schema name. If None, uses configured default.

        Returns:
            str: JSON-formatted string containing table statistics.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError()
        query = f"SHOW STATS FOR {catalog}.{schema}.{table}"
        return self.execute_query(query)

    def optimize(self, table: str, catalog: str | None = None, schema: str | None = None) -> str:
        """Optimize an Iceberg table by compacting small files.

        Args:
            table (str): The name of the table to optimize.
            catalog (Optional[str]): The catalog name. If None, uses configured default.
            schema (Optional[str]): The schema name. If None, uses configured default.

        Returns:
            str: Success message indicating the table was optimized.

        Raises:
            CatalogSchemaError: If either catalog or schema is not specified and not configured.
        """
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError()
        query = f"ALTER TABLE {catalog}.{schema}.{table} EXECUTE optimize"
        self.execute_query(query)
        return f"Table {catalog}.{schema}.{table} optimized successfully"

    def optimize_manifests(self, table: str, catalog: str | None = None, schema: str | None = None) -> str:
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
            raise CatalogSchemaError()
        query = f"ALTER TABLE {catalog}.{schema}.{table} EXECUTE optimize_manifests"
        self.execute_query(query)
        return f"Manifests for table {catalog}.{schema}.{table} optimized successfully"

    def expire_snapshots(
        self,
        table: str,
        retention_threshold: str = "7d",
        catalog: str | None = None,
        schema: str | None = None,
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
