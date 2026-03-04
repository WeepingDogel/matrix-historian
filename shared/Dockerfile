# Multi-stage build for shared package
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy requirements first for better caching
COPY shared/requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy shared package
COPY shared/ /app/

# Install shared package in development mode
RUN uv pip install --system --no-cache -e .

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r historian && useradd -r -g historian historian

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy shared package
COPY shared/ /app/shared/

# Set permissions
RUN chown -R historian:historian /app

USER historian

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

CMD ["python", "-c", "print('Shared package ready')"]
