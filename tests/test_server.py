import json

import httpx2 as httpx
import pytest
from fastmcp.exceptions import ToolError

from mcp_trino import server


async def test_tools_listed_with_annotations(client):
    tools = {t.name: t for t in await client.list_tools()}
    assert {"show_catalogs", "execute_query", "optimize", "show_snapshots"} <= tools.keys()
    assert tools["show_catalogs"].annotations.read_only_hint is True
    assert tools["optimize"].annotations.destructive_hint is True


async def test_discovery(client):
    assert "tpch" in (await client.call_tool("show_catalogs")).data.splitlines()
    assert "tiny" in (await client.call_tool("show_schemas", {"catalog": "tpch"})).data.splitlines()
    tables = (await client.call_tool("show_tables", {"catalog": "tpch", "schema_name": "tiny"})).data
    assert "nation" in tables.splitlines()


async def test_config_defaults_used(client):
    # TRINO_CATALOG/TRINO_SCHEMA = tpch/tiny, so catalog and schema can be omitted
    columns = json.loads((await client.call_tool("describe_table", {"table": "nation"})).data)
    assert "nationkey" in [c["Column"] for c in columns]
    ddl = (await client.call_tool("show_create_table", {"table": "nation"})).data
    assert ddl.startswith("CREATE TABLE tpch.tiny.nation")


async def test_execute_query(client):
    result = await client.call_tool("execute_query", {"query": "SELECT count(*) AS c FROM tpch.tiny.nation"})
    assert json.loads(result.data) == [{"c": 25}]


async def test_trino_error_is_tool_error(client):
    with pytest.raises(ToolError, match="TABLE_NOT_FOUND"):
        await client.call_tool("describe_table", {"table": "does_not_exist"})


async def test_prompts(client):
    prompt = await client.get_prompt("explore_data", {"catalog": "tpch"})
    assert "tpch catalog" in prompt.messages[-1].content.text


async def test_read_only_mode(client, monkeypatch):
    monkeypatch.setattr(server.client.config, "read_only", True)
    server.mcp.disable(tags={"write"})
    try:
        names = {t.name for t in await client.list_tools()}
        assert "optimize" not in names and "execute_query" in names
        with pytest.raises(ToolError, match="read-only"):
            await client.call_tool("execute_query", {"query": "DELETE FROM tpch.tiny.nation"})
        ok = await client.call_tool("execute_query", {"query": "  with t as (select 1 x) select * from t"})
        assert json.loads(ok.data) == [{"x": 1}]
    finally:
        server.mcp.enable(tags={"write"})


async def test_health_route():
    app = server.mcp.http_app()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as http:
        response = await http.get("/health")
    assert response.status_code == 200 and response.json() == {"status": "ok"}
