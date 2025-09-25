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
- Use a virtual environment (venv or conda) for dependency management.

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
