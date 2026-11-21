FROM python:3.12-slim

LABEL io.modelcontextprotocol.server.name="io.github.alaturqua/mcp-trino-python" \
      org.opencontainers.image.source="https://github.com/alaturqua/mcp-trino-python" \
      org.opencontainers.image.description="MCP server for Trino and Iceberg" \
      org.opencontainers.image.licenses="Apache-2.0"

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/

# Dependencies first for layer caching, then the project itself
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project
COPY README.md ./
COPY src/ src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home --uid 1000 mcp
USER mcp

EXPOSE 8000

# stdio by default (what MCP clients spawn); use `--transport http` for a remote server on :8000/mcp
ENTRYPOINT ["mcp-trino"]
CMD ["--transport", "stdio"]
