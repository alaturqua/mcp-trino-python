"""SQL generation tests without a Trino server (the Docker image has no Iceberg catalog)."""

import pytest

from mcp_trino.config import TrinoConfig
from mcp_trino.trino_client import CatalogSchemaError, TrinoClient, TrinoError


class FakeCursor:
    description = [("x",)]

    def __init__(self, log):
        self.log = log

    def execute(self, query):
        self.log.append(query)

    def fetchall(self):
        return []


@pytest.fixture
def fake():
    client = TrinoClient(TrinoConfig(host="localhost", port=8080, user="t", catalog="ice", schema="db"))
    log = []
    client.client.cursor = lambda: FakeCursor(log)
    return client, log


@pytest.mark.parametrize(
    ("method", "suffix"),
    [
        ("show_table_properties", "properties"),
        ("show_table_history", "history"),
        ("show_metadata_log_entries", "metadata_log_entries"),
        ("show_snapshots", "snapshots"),
        ("show_manifests", "manifests"),
        ("show_partitions", "partitions"),
        ("show_files", "files"),
        ("show_entries", "entries"),
        ("show_refs", "refs"),
    ],
)
def test_iceberg_metadata_sql(fake, method, suffix):
    client, log = fake
    getattr(client, method)("cat", "sch", "tbl")
    assert log == [f'SELECT * FROM "cat"."sch"."tbl${suffix}"']


def test_all_snapshots_variants(fake):
    client, log = fake
    client.show_manifests("cat", "sch", "tbl", all_snapshots=True)
    client.show_entries(None, None, "tbl", all_snapshots=True)
    assert log == [
        'SELECT * FROM "cat"."sch"."tbl$all_manifests"',
        'SELECT * FROM "ice"."db"."tbl$all_entries"',
    ]


def test_maintenance_sql(fake):
    client, log = fake
    client.optimize("cat", "sch", "tbl")
    client.optimize_manifests("cat", "sch", "tbl")
    client.expire_snapshots("cat", "sch", "tbl", "30d")
    assert log == [
        'ALTER TABLE "cat"."sch"."tbl" EXECUTE optimize',
        'ALTER TABLE "cat"."sch"."tbl" EXECUTE optimize_manifests',
        """ALTER TABLE "cat"."sch"."tbl" EXECUTE expire_snapshots(retention_threshold => '30d')""",
    ]


def test_expire_snapshots_rejects_injection(fake):
    client, _ = fake
    with pytest.raises(TrinoError):
        client.expire_snapshots("cat", "sch", "tbl", "7d'); DROP TABLE x; --")


def test_identifiers_are_quoted(fake):
    client, log = fake
    client.describe_table("cat", "sch", 'x" ; DROP TABLE y --')
    client.show_snapshots("cat", "sch", 't"')
    assert log == ['DESCRIBE "cat"."sch"."x"" ; DROP TABLE y --"', 'SELECT * FROM "cat"."sch"."t""$snapshots"']


def test_missing_catalog_schema():
    client = TrinoClient(TrinoConfig(host="localhost", port=8080, user="t"))
    with pytest.raises(CatalogSchemaError):
        client.show_snapshots(None, None, "tbl")
