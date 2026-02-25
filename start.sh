#!/bin/bash
# Startup script: seed database then start API server
set -e

echo "=== Seeding database ==="
python -m src.database.seed || echo "Seed warning (non-fatal)"

echo "=== Starting API server on port ${PORT:-8000} ==="
exec uvicorn src.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
