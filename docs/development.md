# Development

## Setup

```bash
git clone https://github.com/alaturqua/mcp-trino-python.git
cd mcp-trino-python
uv sync
```

## Tests

The tests run against a real Trino in Docker:

```bash
docker compose up -d --wait trino
uv run pytest
```

Without a reachable Trino, the server tests are skipped and only the SQL-generation tests run.

## Lint and format

```bash
uv run ruff check
uv run ruff format
```

## Try your changes

```bash
uv run mcp-trino --transport http          # http://localhost:8000/mcp
npx @modelcontextprotocol/inspector         # browse tools and call them by hand
```

## Docs

```bash
uv run --group docs mkdocs serve           # http://127.0.0.1:8000
```

The site is published to GitHub Pages on every push to `main` that touches the docs.

## Project layout

| Path                         | What it is                                                         |
| ---------------------------- | ------------------------------------------------------------------ |
| `src/mcp_trino/server.py`    | MCP tools, prompts and the command-line entry point                |
| `src/mcp_trino/trino_client.py` | SQL generation and query execution                              |
| `src/mcp_trino/config.py`    | Environment variable handling                                      |
| `server.json`                | MCP Registry listing                                               |
| `.claude-plugin/`            | Claude Code plugin and marketplace                                 |
| `mcpb/`                      | Claude Desktop extension manifest and build script                 |

## Releasing

1. Bump `version` in `pyproject.toml` and `.claude-plugin/plugin.json`.
2. Publish a GitHub release tagged `v<version>`.

The `Publish` workflow then pushes the package to PyPI, the image to ghcr.io, the listing to the MCP Registry, and
attaches the Claude Desktop extension to the release. Build the extension locally with `sh mcpb/pack.sh`
(needs `npm install -g @anthropic-ai/mcpb`).
