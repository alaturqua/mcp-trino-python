# Connect your AI client

Every client runs the same command, `uvx mcp-trino-python`, and passes the [connection settings](configuration.md) as
environment variables. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first.

=== "Claude Code"

    **Plugin (recommended).** Claude Code asks for the connection settings when you install it:

    ```text
    /plugin marketplace add alaturqua/mcp-trino-python
    /plugin install trino@mcp-trino-python
    ```

    **Or add the server directly:**

    ```bash
    claude mcp add trino -e TRINO_HOST=localhost -e TRINO_USER=trino -- uvx mcp-trino-python
    ```

=== "Claude Desktop"

    **One-click extension (recommended).**

    1. Download `mcp-trino-python.mcpb` from the
       [latest release](https://github.com/alaturqua/mcp-trino-python/releases/latest).
    2. Double-click it, or drag it into **Settings → Extensions**.
    3. Fill in your Trino host and user when asked.

    **Or edit `claude_desktop_config.json`** (Settings → Developer → Edit Config):

    ```json
    {
      "mcpServers": {
        "trino": {
          "command": "uvx",
          "args": ["mcp-trino-python"],
          "env": { "TRINO_HOST": "localhost", "TRINO_PORT": "8080", "TRINO_USER": "trino" }
        }
      }
    }
    ```

=== "VS Code / GitHub Copilot"

    Create `.vscode/mcp.json` in your workspace, or run **MCP: Add Server** from the command palette:

    ```json
    {
      "servers": {
        "trino": {
          "type": "stdio",
          "command": "uvx",
          "args": ["mcp-trino-python"],
          "env": { "TRINO_HOST": "localhost", "TRINO_PORT": "8080", "TRINO_USER": "trino" }
        }
      }
    }
    ```

    Open Copilot Chat in **Agent** mode; the Trino tools appear in the tools list.

    For the **GitHub Copilot CLI**, put the same entry under `mcpServers` in `~/.copilot/mcp-config.json`.

=== "Cursor, Windsurf and others"

    Most clients use the `mcpServers` format, for example `~/.cursor/mcp.json`:

    ```json
    {
      "mcpServers": {
        "trino": {
          "command": "uvx",
          "args": ["mcp-trino-python"],
          "env": { "TRINO_HOST": "localhost", "TRINO_PORT": "8080", "TRINO_USER": "trino" }
        }
      }
    }
    ```

    The server is also in the [MCP Registry](https://registry.modelcontextprotocol.io) as
    `io.github.alaturqua/mcp-trino-python`, so clients that browse the registry can install it from there.

=== "Docker"

    Clients that start the server themselves can run the container instead of `uvx`:

    ```json
    {
      "mcpServers": {
        "trino": {
          "command": "docker",
          "args": ["run", "-i", "--rm", "-e", "TRINO_HOST", "-e", "TRINO_USER", "ghcr.io/alaturqua/mcp-trino-python"],
          "env": { "TRINO_HOST": "host.docker.internal", "TRINO_USER": "trino" }
        }
      }
    }
    ```

    `host.docker.internal` reaches a Trino running on your own machine.

## Troubleshooting

`uvx: command not found`
:   Install uv, then restart your client so it picks up the new `PATH`.

The tools don't show up
:   Restart the client after changing its config. In Claude Code, `/mcp` shows the server's status and errors.

`Connection refused` or timeouts
:   Check `TRINO_HOST` and `TRINO_PORT`. Inside Docker, `localhost` is the container itself; use
    `host.docker.internal` or the Trino container's name.

`Both catalog and schema must be specified`
:   Mention the catalog and schema in your question, or set `TRINO_CATALOG` and `TRINO_SCHEMA`.
