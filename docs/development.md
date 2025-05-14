# Development Guide

{% hint style="info" %}
**Category**: Development
{% endhint %}

## Setup

- Recommended Python version: 3.12 or higher.
- Use a virtual environment (venv or conda) for dependency management.

## Code Standards

- Follow PEP8 style guidelines.
- Use the built-in logging module for logging.
- Test the project with pytest:
   ```bash
   pytest
   ```

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
