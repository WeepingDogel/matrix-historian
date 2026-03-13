# Development Guide

This guide reflects the current repository structure on the main branch.

## Repository layout

```text
matrix-historian/
├── docker-compose.yml
├── docker-compose.production.yml
├── docker-compose.staging.yml
├── .env.example
├── docs/
├── services/
│   ├── api/
│   ├── bot/
│   └── web/
├── shared/
└── tests/
```

## Tech stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- MinIO

### Frontend
- SvelteKit
- Vite
- Tailwind CSS / DaisyUI
- Chart.js

## Local development

### Backend setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e ./shared
pip install -r services/api/requirements.txt
pip install -r services/bot/requirements.txt
```

### Frontend setup

```bash
cd services/web
npm install
```

## Running local services

You can use Docker Compose for infrastructure plus local app processes, or run the full stack in Docker.

### Option A: Full stack with Docker Compose

```bash
docker-compose up -d --build
```

### Option B: Run app processes locally

Start infrastructure first if needed:

```bash
docker-compose up -d db minio
```

Then run services:

```bash
# terminal 1
cd services/api/app
uvicorn main:app --reload --port 8000

# terminal 2
cd services/bot/app
python main.py

# terminal 3
cd services/web
npm run dev
```

## Frontend-specific notes

The web frontend lives in `services/web/`.

Current frontend responsibilities include:
- archive browsing and analytics UI
- language switching (`en`, `zh-CN`)
- timezone display switching (`Local`, `UTC`)
- formatting UTC timestamps for browser display

Important: timestamps remain UTC in API/database data; conversion is done for presentation in the browser.

## Useful frontend commands

```bash
cd services/web
npm run dev
npm run build
npm run preview
npm run check
```

## Useful backend commands

```bash
# API logs in Docker
docker-compose logs -f api

# Bot logs in Docker
docker-compose logs -f bot
```

## Testing

```bash
pytest
```

For frontend validation:

```bash
cd services/web
npm run check
```

## Contributing expectations

When changing user-facing behavior, update docs accordingly.

Examples:
- new environment variables
- port changes
- web UI behavior
- timezone display rules
- supported languages
