"""Client for interacting with Trino, including Iceberg table operations."""

import json
import re

import trino

from .config import TrinoConfig

# shortcut: keyword check, not a SQL parser; the real guarantee is a read-only Trino user or access control.
_READ_ONLY_SQL = re.compile(r"^\s*(\(\s*)*(SELECT|WITH|SHOW|DESCRIBE|EXPLAIN|VALUES)\b", re.IGNORECASE)


class TrinoError(Exception):
    """Base class for Trino-related errors."""


class CatalogSchemaError(TrinoError):
    """Raised when catalog or schema is missing and has no configured default."""

    def __init__(self, message: str = "Both catalog and schema must be specified"):
        super().__init__(message)


class ReadOnlyError(TrinoError):
    """Raised when a write statement is sent while read-only mode is on."""


class TrinoClient:
    """Executes queries and maintenance operations on a Trino server."""

    def __init__(self, config: TrinoConfig):
        self.config = config
        self.client = trino.dbapi.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            catalog=config.catalog,
            schema=config.schema,
            http_scheme=config.http_scheme,
            auth=config.auth,
            source=config.source,
        )

    def _rows(self, query: str) -> list[dict] | None:
        """Run a query; None means the statement returns no result set (e.g. ALTER)."""
        if self.config.read_only and not _READ_ONLY_SQL.match(query):
            raise ReadOnlyError("Server is in read-only mode (TRINO_READ_ONLY); only read statements are allowed")
        cur = self.client.cursor()
        cur.execute(query)
        if not cur.description:
            return None
        columns = [col[0] for col in cur.description]
        return [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]

    def _resolve(self, catalog: str | None, schema: str | None) -> tuple[str, str]:
        catalog = catalog or self.config.catalog
        schema = schema or self.config.schema
        if not catalog or not schema:
            raise CatalogSchemaError
        return catalog, schema

    def _metadata(self, catalog: str | None, schema: str | None, table: str, suffix: str) -> str:
        """Query an Iceberg metadata table such as ``table$snapshots``."""
        catalog, schema = self._resolve(catalog, schema)
        return self.execute_query(f'SELECT * FROM {catalog}.{schema}."{table}${suffix}"')

    def execute_query(self, query: str) -> str:
        """Execute a SQL query and return the rows as a JSON string."""
        rows = self._rows(query)
        if rows is None:
            return "Query executed successfully (no results to display)"
        return json.dumps(rows, default=str)

    def get_query_history(self, limit: int | None = None) -> str:
        query = "SELECT * FROM system.runtime.queries ORDER BY created DESC"
        if limit is not None:
            query += f" LIMIT {int(limit)}"
        return self.execute_query(query)

    def list_catalogs(self) -> str:
        return "\n".join(row["Catalog"] for row in self._rows("SHOW CATALOGS"))

    def list_schemas(self, catalog: str | None) -> str:
        catalog = catalog or self.config.catalog
        if not catalog:
            raise CatalogSchemaError("Catalog must be specified")
        return "\n".join(row["Schema"] for row in self._rows(f"SHOW SCHEMAS FROM {catalog}"))

    def list_tables(self, catalog: str | None, schema: str | None) -> str:
        catalog, schema = self._resolve(catalog, schema)
        return "\n".join(row["Table"] for row in self._rows(f"SHOW TABLES FROM {catalog}.{schema}"))

    def describe_table(self, catalog: str | None, schema: str | None, table: str) -> str:
        catalog, schema = self._resolve(catalog, schema)
        return self.execute_query(f"DESCRIBE {catalog}.{schema}.{table}")

    def show_create_table(self, catalog: str | None, schema: str | None, table: str) -> str:
        catalog, schema = self._resolve(catalog, schema)
        rows = self._rows(f"SHOW CREATE TABLE {catalog}.{schema}.{table}")
        return rows[0]["Create Table"] if rows else ""

    def show_create_view(self, catalog: str | None, schema: str | None, view: str) -> str:
        catalog, schema = self._resolve(catalog, schema)
        rows = self._rows(f"SHOW CREATE VIEW {catalog}.{schema}.{view}")
        return rows[0]["Create View"] if rows else ""

    def show_stats(self, catalog: str | None, schema: str | None, table: str) -> str:
        catalog, schema = self._resolve(catalog, schema)
        return self.execute_query(f"SHOW STATS FOR {catalog}.{schema}.{table}")

    def optimize(self, catalog: str | None, schema: str | None, table: str) -> str:
        catalog, schema = self._resolve(catalog, schema)
        self._rows(f"ALTER TABLE {catalog}.{schema}.{table} EXECUTE optimize")
        return f"Table {catalog}.{schema}.{table} optimized successfully"

    def optimize_manifests(self, catalog: str | None, schema: str | None, table: str) -> str:
        catalog, schema = self._resolve(catalog, schema)
        self._rows(f"ALTER TABLE {catalog}.{schema}.{table} EXECUTE optimize_manifests")
        return f"Manifests for table {catalog}.{schema}.{table} optimized successfully"

    def expire_snapshots(
        self, catalog: str | None, schema: str | None, table: str, retention_threshold: str = "7d"
    ) -> str:
        catalog, schema = self._resolve(catalog, schema)
        if not re.fullmatch(r"\d+(\.\d+)?(ns|us|ms|s|m|h|d)", retention_threshold):
            raise TrinoError(f"Invalid retention_threshold {retention_threshold!r}; expected e.g. '7d' or '12h'")
        self._rows(
            f"ALTER TABLE {catalog}.{schema}.{table} "
            f"EXECUTE expire_snapshots(retention_threshold => '{retention_threshold}')"
        )
        return f"Snapshots older than {retention_threshold} expired for table {catalog}.{schema}.{table}"

    def show_catalog_tree(self) -> str:
        tree = []
        for catalog in sorted(row["Catalog"] for row in self._rows("SHOW CATALOGS")):
            tree.append(catalog)
            try:
                for schema in sorted(row["Schema"] for row in self._rows(f"SHOW SCHEMAS FROM {catalog}")):
                    tree.append(f"  {schema}")
                    try:
                        tables = self._rows(f"SHOW TABLES FROM {catalog}.{schema}")
                        tree.extend(f"    {t}" for t in sorted(row["Table"] for row in tables))
                    except (trino.exceptions.TrinoQueryError, KeyError):
                        tree.append("    (unable to list tables)")
            except (trino.exceptions.TrinoQueryError, KeyError):
                tree.append("  (unable to list schemas)")
        return "\n".join(tree) if tree else "No catalogs found"

    def show_table_properties(self, catalog: str | None, schema: str | None, table: str) -> str:
        return self._metadata(catalog, schema, table, "properties")

    def show_table_history(self, catalog: str | None, schema: str | None, table: str) -> str:
        return self._metadata(catalog, schema, table, "history")

    def show_metadata_log_entries(self, catalog: str | None, schema: str | None, table: str) -> str:
        return self._metadata(catalog, schema, table, "metadata_log_entries")

    def show_snapshots(self, catalog: str | None, schema: str | None, table: str) -> str:
        return self._metadata(catalog, schema, table, "snapshots")

    def show_manifests(self, catalog: str | None, schema: str | None, table: str, all_snapshots: bool = False) -> str:
        return self._metadata(catalog, schema, table, "all_manifests" if all_snapshots else "manifests")

    def show_partitions(self, catalog: str | None, schema: str | None, table: str) -> str:
        return self._metadata(catalog, schema, table, "partitions")

    def show_files(self, catalog: str | None, schema: str | None, table: str) -> str:
        return self._metadata(catalog, schema, table, "files")

    def show_entries(self, catalog: str | None, schema: str | None, table: str, all_snapshots: bool = False) -> str:
        return self._metadata(catalog, schema, table, "all_entries" if all_snapshots else "entries")

    def show_refs(self, catalog: str | None, schema: str | None, table: str) -> str:
        return self._metadata(catalog, schema, table, "refs")
