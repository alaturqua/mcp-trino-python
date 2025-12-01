FROM python:3.12-slim

WORKDIR /app

# Environment variables
ENV UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Copy source code
COPY src/ src/

ENV PATH="/app/.venv/bin:$PATH"

# Default port for HTTP transports
EXPOSE 8000

# Default transport is stdio for MCP compatibility
# Override with --transport streamable-http or --transport sse for HTTP modes
ENTRYPOINT ["uv", "run", "src/server.py"]

# Default arguments (can be overridden)
# For stdio (default MCP transport): no args needed
# For HTTP: --transport streamable-http --host 0.0.0.0 --port 8000
CMD ["--transport", "stdio"]