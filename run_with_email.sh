#!/bin/bash
# Wrapper script to run DeMark scanner and send results via email

set -e

cd "$(dirname "$0")" || exit 1

echo "Starting DeMark Scanner with Email Results..."
echo "=============================================="

# Activate venv and sync
source .venv/bin/activate
uv sync

# Run the scanner with email
python send_email_results.py

echo "Done!"
