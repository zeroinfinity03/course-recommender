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

# Copy entrypoint script and make executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# SageMaker runs: docker run <image> serve
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["serve"]

