# Use a Python image with uv pre-installed
FROM python:3.12-slim

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

ADD . /app

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT [ "uv", "run", "mcp", "run", "src/server.py" ]