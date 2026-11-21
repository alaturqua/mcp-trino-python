"""Configuration module for Trino connection settings."""

import os
from dataclasses import dataclass

import trino
from dotenv import load_dotenv


@dataclass
class TrinoConfig:
    """Configuration class for Trino connection settings."""

    host: str
    port: int
    user: str
    catalog: str | None = None
    schema: str | None = None
    http_scheme: str = "http"
    auth: trino.auth.BasicAuthentication | None = None
    source: str = "mcp-trino-python"
    read_only: bool = False


def load_config() -> TrinoConfig:
    """Load Trino configuration from environment variables (and a .env file, which never overrides them)."""
    load_dotenv()

    # Marketplace clients pass unset optional fields as empty strings, so treat "" as unset.
    def env(name: str, default: str | None = None) -> str | None:
        return os.getenv(name) or default

    user = env("TRINO_USER", env("USER", "trino"))
    password = env("TRINO_PASSWORD")
    return TrinoConfig(
        host=env("TRINO_HOST", "localhost"),
        port=int(env("TRINO_PORT", "8080")),
        user=user,
        catalog=env("TRINO_CATALOG"),
        schema=env("TRINO_SCHEMA"),
        http_scheme=env("TRINO_HTTP_SCHEME", "http"),
        auth=trino.auth.BasicAuthentication(user, password) if password else None,
        read_only=env("TRINO_READ_ONLY", "false").lower() in ("1", "true", "yes"),
    )
