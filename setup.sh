#!/usr/bin/env bash
# One-command setup for the Agents Bootcamp on macOS / Linux.
# Run from the repo root:  ./setup.sh
set -e

echo ""
echo "=== Agents Bootcamp setup (macOS / Linux) ==="
echo ""

# Prefer python3, fall back to python.
PY=python3
command -v python3 >/dev/null 2>&1 || PY=python
if ! command -v "$PY" >/dev/null 2>&1; then
    echo "Python 3.10+ was not found. Install it from https://www.python.org/downloads/"
    echo "and run ./setup.sh again."
    exit 1
fi

echo "[1/3] Creating virtual environment (.venv)..."
"$PY" -m venv .venv

echo "[2/3] Installing the harness and all dependencies..."
.venv/bin/python -m pip install --upgrade pip >/dev/null
.venv/bin/python -m pip install -e .

echo "[3/3] Verifying your setup..."
# '|| true' so a missing-key message doesn't stop the closing instructions below.
.venv/bin/python check_setup.py || true

echo ""
echo "Setup complete."
echo "If a .env file was just created, open it, paste your keys, then run:"
echo "    .venv/bin/python check_setup.py"
echo ""
echo "To work on the assignments, activate the environment in each new terminal:"
echo "    source .venv/bin/activate"
