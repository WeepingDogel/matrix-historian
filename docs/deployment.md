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
   cd matrix-historian
   ```
2. Build the API image:
   ```bash
   docker build -f src/Dockerfile -t matrix-historian-api .
   ```
3. Build the Web UI image:
   ```bash
   docker build -f src/app/webui/Dockerfile -t matrix-historian-webui .
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

1. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install dependencies:
   ```bash
   # Using uv pip install with package list
   uv pip install matrix-nio==0.24.0 simplematrixbotlib==2.12.3 h11==0.14.0 httpcore==0.17.3 fastapi==0.115.12 uvicorn==0.34.2 sqlalchemy==2.0.40 python-multipart==0.0.20 pydantic==2.11.4 email-validator==2.2.0 pytest==8.3.5 python-dotenv==1.1.0 backoff==2.2.1 groq pandas==2.2.3 plotly==5.20.0 jieba==0.42.1 networkx==3.2.1
   
   # Or create a virtual environment and install
   uv venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   pip install -r ../src/requirements.txt
   ```

3. Start the FastAPI service:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. Launch the Matrix Bot and Web UI separately (e.g., using Streamlit):
   ```bash
   streamlit run app/webui/main.py --server.port=8501 --server.address=0.0.0.0
   ```

5. Ensure all environment variables in the `.env` file are properly configured.

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
- Python 3.12+

## Dependencies

The project uses **uv** for dependency management. All dependencies are defined in `pyproject.toml`:
- Matrix Bot libraries (matrix-nio, simplematrixbotlib)
- FastAPI and uvicorn
- Streamlit for web UI
- pandas, plotly, networkx, wordcloud, matplotlib, jieba for analysis
- Groq for AI-powered features

Builds use uv for faster, more reliable dependency resolution.

