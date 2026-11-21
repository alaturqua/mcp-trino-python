# MCP Trino Server

Let your AI assistant talk to [Trino](https://trino.io). Ask questions about your data in plain language, and the
assistant explores catalogs, writes and runs SQL, and inspects or maintains your Iceberg tables for you.

It works with **Claude Code**, **Claude Desktop**, **GitHub Copilot in VS Code**, and any other client that speaks the
[Model Context Protocol (MCP)](https://modelcontextprotocol.io).

<div class="grid cards" markdown>

-   **Explore**

    List catalogs, schemas and tables, describe columns, show DDL and statistics.

-   **Query**

    Run SQL and get the rows back as JSON.

-   **Iceberg**

    Inspect snapshots, manifests, partitions, files and history. Compact files and expire snapshots.

-   **Read-only mode**

    One setting blocks writes and hides the maintenance tools.

</div>

## Try it in two minutes

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/). It runs the server, so there is no
   Python setup to do.
2. Add the server to your AI client. For Claude Code:

    ```bash
    claude mcp add trino -e TRINO_HOST=localhost -e TRINO_USER=trino -- uvx mcp-trino-python
    ```

    Other clients: see [Connect your AI client](clients.md).

3. Ask: *"What catalogs are in Trino?"*

No Trino server at hand? [Start one locally with Docker](getting-started.md#run-trino-locally).

## What you can ask

- "Show me the tables in `iceberg.sales` and describe the biggest one."
- "Which customers placed the most orders last quarter?"
- "When was `iceberg.sales.orders` last compacted? Show its snapshots."
- "Expire snapshots older than 30 days on `iceberg.sales.orders`."
