#!/bin/sh
set -e

# SageMaker runs: docker run <image> serve
if [ "${1:-}" = "serve" ]; then
  exec uv run uvicorn app:app --host 0.0.0.0 --port 8080
fi

# If anything else is passed, run it as a command
exec "$@"
