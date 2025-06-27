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
   docker-compose up -d
   ```
   - API Service will be accessible at: http://localhost:8001
   - Web Interface will be accessible at: http://localhost:8502

### Running Manually

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   .venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```bash
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

5. Launch the Streamlit web interface:
   ```bash
   streamlit run app/webui/main.py --server.port=8501 --server.address=0.0.0.0
   ```
