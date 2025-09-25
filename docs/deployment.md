# Category
* [Overview](./overview.md)
* [Get Started](./get-started.md)
* [Deployment](./deployment.md)
* [Development](./development.md)
* [API Reference](./reference/api-reference.md)

# Deployment Guide

## Docker Deployment

### Build Docker Images

1. Navigate to the source directory:
   ```bash
   cd matrix-historian/src
   ```
2. Build the API image (uses `src/Dockerfile`):
   ```bash
   docker build -f Dockerfile -t matrix-historian-api .
   ```
3. Build the Web UI image (uses `src/app/webui/Dockerfile`):
   ```bash
   docker build -f Dockerfile.webui -t matrix-historian-webui .
   ```

### Launch with docker-compose

Start all services using the docker-compose file located under `src/`:
```bash
docker-compose up -d
```
Service configuration (as defined in `src/docker-compose.yml`):
- API service runs on port 8000 (mapped to host port 8001).
- Web UI service runs on port 8501 (mapped to host port 8502).
- The database volume is mounted at `/app/app/db` inside the API container for data persistence.

## Manual Deployment

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI service:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
3. Launch the Matrix Bot and Web UI separately (e.g., using Streamlit):
   ```bash
   streamlit run app/webui/main.py --server.port=8501 --server.address=0.0.0.0
   ```
4. Ensure all environment variables in the `.env` file are properly configured.

## Reverse Proxy Configuration (Example with Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:8502/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## HTTPS Configuration (Example with Let's Encrypt)

1. Install Certbot:
   ```bash
   sudo apt-get update
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. Obtain a certificate:
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

3. Update your Nginx configuration to redirect HTTP to HTTPS.

## Troubleshooting

- Verify that the `.env` file contains valid Matrix configuration.
- Use `docker logs <container_name>` to inspect container logs if issues arise.
- Confirm that the required ports are available and not conflicted by other applications.

## AI Analysis Configuration

To enable AI analysis features (sentiment analysis, etc.), you need to:

1. Register and obtain a Groq API key
2. Set the environment variable:
   ```bash
   GROQ_API_KEY=your_api_key_here
   ```

## System Requirements

In addition to basic requirements, for analysis features we recommend:

- CPU: 4+ cores
- Memory: 8GB+ RAM
- Disk: 20GB+ storage
- Python 3.9+

## Dependencies

New analysis features require:
- pandas
- plotly
- networkx
- wordcloud
- matplotlib
- jieba

