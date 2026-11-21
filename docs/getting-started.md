# Getting started

## What you need

- A Trino server you can reach, or Docker to [run one locally](#run-trino-locally).
- [uv](https://docs.astral.sh/uv/getting-started/installation/). It downloads the right Python and the server for you.

Check that the server starts:

```bash
uvx mcp-trino-python --help
```

## Run Trino locally

To try things out, run Trino with its built-in sample data (TPC-H and TPC-DS):

```bash
docker run -d --name trino -p 8080:8080 trinodb/trino:484
```

Give it about 30 seconds to start. Then point the server at `localhost:8080` with user `trino`.
The sample data is in catalog `tpch`, in schemas such as `tiny` and `sf1`.

## Connect your AI client

Pick your client on the [Connect your AI client](clients.md) page. For Claude Code:

```bash
claude mcp add trino \
  -e TRINO_HOST=localhost -e TRINO_USER=trino \
  -e TRINO_CATALOG=tpch -e TRINO_SCHEMA=tiny \
  -- uvx mcp-trino-python
```

`TRINO_CATALOG` and `TRINO_SCHEMA` are optional. With them set, the assistant can leave the catalog and schema out of
its tool calls.

## First questions to ask

- "What catalogs and schemas are there?"
- "Describe the `orders` table."
- "What are the top 5 nations by number of customers?"

!!! tip "Working with production data?"
    Set `TRINO_READ_ONLY=true` so the assistant can only read. See [Read-only mode](configuration.md#read-only-mode).
