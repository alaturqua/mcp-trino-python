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


def load_config() -> TrinoConfig:
    """Load Trino configuration from environment variables."""
    load_dotenv(override=True)

    return TrinoConfig(
        host=os.getenv("TRINO_HOST", "localhost"),
        port=int(os.getenv("TRINO_PORT", "8080")),
        user=os.getenv("TRINO_USER", os.getenv("USER", "trino")),
        catalog=os.getenv("TRINO_CATALOG"),
        schema=os.getenv("TRINO_SCHEMA"),
        http_scheme=os.getenv("TRINO_HTTP_SCHEME", "http"),
        auth=None
        if os.getenv("TRINO_PASSWORD", None) is None
        else trino.auth.BasicAuthentication(os.getenv("TRINO_USER", None), os.getenv("TRINO_PASSWORD", None)),
        source="mcp-trino-python",
    )
