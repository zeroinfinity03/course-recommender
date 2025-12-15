# Use Python 3.11 (Matches your project)
FROM python:3.11-slim

# Install 'uv' package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy config files
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy source code and model artifacts
COPY src/app.py .
COPY src/reco_artifacts.joblib .

# SageMaker runs on Port 8080
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
