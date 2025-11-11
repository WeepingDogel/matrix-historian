# Category
* [Overview](./overview.md)
* [Get Started](./get-started.md)
* [Deployment](./deployment.md)
* [Development](./development.md)
* [API Reference](./reference/api-reference.md)

---


# Development Guide

## Setup

- Recommended Python version: 3.12 or higher.
- The project uses **uv** for dependency management.
- Dependencies are defined in `pyproject.toml` at the project root.

### Installing Dependencies

1. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install project dependencies:
   ```bash
   # Using uv pip install
   uv pip install matrix-nio==0.24.0 simplematrixbotlib==2.12.3 h11==0.14.0 httpcore==0.17.3 fastapi==0.115.12 uvicorn==0.34.2 sqlalchemy==2.0.40 python-multipart==0.0.20 pydantic==2.11.4 email-validator==2.2.0 pytest==8.3.5 python-dotenv==1.1.0 backoff==2.2.1 groq pandas==2.2.3 plotly==5.20.0 jieba==0.42.1 networkx==3.2.1
   
   # Or using traditional pip
   pip install -r ../src/requirements.txt
   ```

## Code Standards

- Follow PEP8 style guidelines.
- Use the built-in logging module for logging.
 - All API routes are mounted under `/api/v1`; analytics routes are nested under `/api/v1/analytics`.

## Project Structure

```
src/
├── app/             # Main application code
│   ├── api/        # API endpoints
│   ├── bot/        # Matrix bot logic
│   ├── db/         # Database models and utilities
│   ├── crud/       # Database CRUD operations
│   ├── schemas/    # Data validation schemas
│   ├── utils/      # Utility functions
│   └── webui/      # Web interface
├── tests/          # Test code
├── docs/           # Documentation
└── docker-compose.yml
```

## Debugging

- FastAPI supports auto-reload for development.
- Streamlit automatically refreshes the interface.
- Refer to `app/utils/logging_config.py` for logging configuration details.
 - The app launches a background Matrix bot task via `MatrixBot` during FastAPI lifespan; be mindful of async behavior when debugging.
