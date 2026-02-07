FROM python:3.12-slim

WORKDIR /app

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package first
COPY shared/ /app/shared/

# Install shared package dependencies
RUN uv pip install --system --no-cache -e /app/shared/

# Copy bot service
COPY services/bot/requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY services/bot/app/ /app/

# Run the bot
CMD ["python", "main.py"]
