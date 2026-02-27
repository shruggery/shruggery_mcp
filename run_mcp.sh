#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Create venv if missing
if [ ! -d .venv ]; then
    python3 -m venv .venv
    .venv/bin/pip install -e .
fi

exec .venv/bin/python -m shruggery
