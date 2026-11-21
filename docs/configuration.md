# Configuration

The server is configured with environment variables. Your AI client passes them (the `env` block in its config), or
you can put them in a `.env` file in the working directory. Real environment variables win over `.env`.

## Trino connection

| Variable            | What it does                                            | Default     |
| ------------------- | ------------------------------------------------------- | ----------- |
| `TRINO_HOST`        | Trino server hostname                                   | `localhost` |
| `TRINO_PORT`        | Trino server port                                       | `8080`      |
| `TRINO_USER`        | User to run queries as                                  | `trino`     |
| `TRINO_PASSWORD`    | Password; turns on basic authentication                 | not set     |
| `TRINO_HTTP_SCHEME` | `http` or `https`                                       | `http`      |
| `TRINO_CATALOG`     | Default catalog when a tool call leaves it out          | not set     |
| `TRINO_SCHEMA`      | Default schema when a tool call leaves it out           | not set     |
| `TRINO_READ_ONLY`   | `true` blocks writes and hides maintenance tools        | `false`     |

!!! warning "Passwords need https"
    Trino only accepts passwords over https, so set `TRINO_HTTP_SCHEME=https` together with `TRINO_PASSWORD`.

## Read-only mode

With `TRINO_READ_ONLY=true`:

- `optimize`, `optimize_manifests` and `expire_snapshots` are hidden from the assistant.
- `execute_query` only runs statements that start with `SELECT`, `WITH`, `SHOW`, `DESCRIBE`, `EXPLAIN` or `VALUES`.

This is a guard rail against mistakes, not a security boundary: it looks at the first keyword and does not parse the
SQL. To be sure nothing can be changed, connect as a Trino user that only has read permissions.

## Server options

These matter only when you run the server over HTTP (see [Remote and Docker deployment](deployment.md)).

| Flag          | Variable        | What it does                                    | Default     |
| ------------- | --------------- | ----------------------------------------------- | ----------- |
| `--transport` | `MCP_TRANSPORT` | `stdio`, `http`, or `sse` (legacy)              | `stdio`     |
| `--host`      | `MCP_HOST`      | Address to listen on                            | `127.0.0.1` |
| `--port`      | `MCP_PORT`      | Port to listen on                               | `8000`      |
