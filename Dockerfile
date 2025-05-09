FROM python:3.12-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

ADD . /app

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT [ "uv", "run", "src/server.py" ]
CMD [ "--host", "0.0.0.0", "--port", "8000" ]   