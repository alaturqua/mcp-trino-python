"""Tests run against a real Trino: `docker compose up -d --wait trino`."""

import os
import socket

import pytest

os.environ.setdefault("TRINO_HOST", "localhost")
os.environ.setdefault("TRINO_PORT", "8080")
os.environ.setdefault("TRINO_USER", "trino")
os.environ.setdefault("TRINO_CATALOG", "tpch")
os.environ.setdefault("TRINO_SCHEMA", "tiny")


def _trino_up() -> bool:
    try:
        socket.create_connection((os.environ["TRINO_HOST"], int(os.environ["TRINO_PORT"])), timeout=2).close()
        return True
    except OSError:
        return False


@pytest.fixture
async def client():
    if not _trino_up():
        pytest.skip("Trino not reachable; run `docker compose up -d --wait trino`")
    from fastmcp import Client

    from mcp_trino.server import mcp

    async with Client(mcp) as c:
        yield c
