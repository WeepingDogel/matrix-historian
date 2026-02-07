FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package first
COPY shared/ /app/shared/

# Install shared package dependencies
RUN pip install --no-cache-dir -e /app/shared/

# Copy bot service
COPY services/bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/bot/app/ /app/

# Run the bot
CMD ["python", "main.py"]
