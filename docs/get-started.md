# Category
* [Overview](./overview.md)
* [Get Started](./get-started.md)
* [Deployment](./deployment.md)
* [Development](./development.md)
* [API Reference](./reference/api-reference.md)

---

# Quick Start Guide

## Prerequisites
- Docker and docker-compose installed (optional)
- Python 3.12 or higher
- Git installed

## Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/matrix-historian.git
   cd matrix-historian/src
   ```

2. Configure Environment Variables:

   Copy `.env.example` to `.env` and update the values:
   ```bash
   cp .env.example .env
   # Edit .env to set MATRIX_HOMESERVER, MATRIX_USER, MATRIX_PASSWORD, etc.
   ```

3. Deploy the Application:

### Using Docker
   ```bash
   docker-compose -f src/docker-compose.yml up -d
   ```
   - API Service will be accessible at: http://localhost:8001 (proxies to container port 8000)
   - Web interface: removed (API-only deployment)

### Running Manually

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   .venv\Scripts\activate  # On Windows
   ```

2. Install uv and dependencies:
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install project dependencies using uv (API + analysis)
   uv pip install matrix-nio==0.24.0 simplematrixbotlib==2.12.3 h11==0.14.0 httpcore==0.17.3 fastapi==0.115.12 uvicorn==0.34.2 sqlalchemy==2.0.40 python-multipart==0.0.20 pydantic==2.11.4 email-validator==2.2.0 pytest==8.3.5 python-dotenv==1.1.0 backoff==2.2.1 groq pandas==2.2.3 plotly==5.20.0 jieba==0.42.1 networkx==3.2.1
   
   # Or using traditional pip
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python app/db/database.py
   ```

4. Start the FastAPI service:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

5. Web UI

   The Streamlit web UI has been removed from this repository. Use the API
   endpoints (`GET /api/v1/...`) to access messages and analytics. See
   `docs/reference/api-reference.md` for details.

## API Base Path

All HTTP endpoints are mounted under `/api/v1` per the application router configuration.
