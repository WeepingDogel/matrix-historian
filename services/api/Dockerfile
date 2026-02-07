FROM python:3.12-slim

WORKDIR /app

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package first
COPY shared/ /app/shared/

# Install shared package dependencies
RUN uv pip install --system --no-cache -e /app/shared/

# Copy API service
COPY services/api/requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY services/api/app/ /app/

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
