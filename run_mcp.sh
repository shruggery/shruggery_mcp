#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Auto-detect architecture for venv selection
if [ "$(uname -m)" = "arm64" ]; then
    VENV=".venv_laptop"
else
    VENV=".venv"
fi

# Create venv if missing
if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -e .
fi

exec "$VENV/bin/python" -m shruggery
