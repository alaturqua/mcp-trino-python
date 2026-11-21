#!/usr/bin/env sh
# Build the Claude Desktop extension: dist/mcp-trino-python.mcpb
# Usage: sh mcpb/pack.sh   (needs: npm install -g @anthropic-ai/mcpb)
set -eu
cd "$(dirname "$0")/.."
rm -rf build/mcpb && mkdir -p build/mcpb dist
cp mcpb/manifest.json pyproject.toml uv.lock .python-version README.md LICENSE build/mcpb/
cp -r src build/mcpb/src
find build/mcpb \( -name __pycache__ -o -name "*.egg-info" \) -type d -prune -exec rm -rf {} +
mcpb validate build/mcpb/manifest.json
mcpb pack build/mcpb dist/mcp-trino-python.mcpb
