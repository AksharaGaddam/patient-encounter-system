#!/usr/bin/env sh
set -e

# Run migrations then start uvicorn
python -m scripts.run_migrations

# Start the app
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
