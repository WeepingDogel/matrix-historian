# Deployment Guide

This document describes the current repository deployment shape.

## Default deployment mode

The repository is currently set up around Docker Compose and five services:

- `db` — PostgreSQL
- `minio` — S3-compatible media storage
- `bot` — Matrix ingestion/archival service
- `api` — FastAPI backend
- `web` — SvelteKit frontend

## Quick deploy

```bash
git clone https://github.com/WeepingDogel/matrix-historian.git
cd matrix-historian
cp .env.example .env
# edit .env
docker-compose up -d --build
```

## Default published ports

| Service | Port |
|---|---:|
| Web UI | `3000` |
| API | `8500` |
| MinIO API | `9000` |
| MinIO Console | `9001` |

## Important environment variables

```env
MATRIX_HOMESERVER=https://matrix.org
MATRIX_USER=@yourbot:matrix.org
MATRIX_PASSWORD=your_bot_password
DATABASE_URL=postgresql://<db_user>:<db_password>@db:5432/historian
API_PORT=8500
WEB_PORT=3000
MINIO_ROOT_USER=<minio_admin_user>
MINIO_ROOT_PASSWORD=<minio_admin_password>
MINIO_ENDPOINT=minio:9000
MINIO_BUCKET=matrix-media
MINIO_PUBLIC_URL=
GROQ_API_KEY=
```

## Service notes

### db
Stores archived messages and metadata in PostgreSQL.

### minio
Stores archived media objects. `MINIO_PUBLIC_URL` can be configured when media URLs need to be externally reachable.

### bot
Logs into Matrix and archives events. It depends on healthy `db` and `minio` services.

### api
Provides `/health`, `/docs`, and `/api/v1/*` endpoints.

### web
Hosts the browser UI and talks to the API service via `API_URL=http://api:8000` in Docker.

## Timezone and language behavior in deployment

Current behavior is intentional:

- backend/database timestamps are stored in **UTC**
- frontend displays timestamps in **Local** or **UTC**
- frontend supports `en` and `zh-CN`

So if you see local-time rendering in the UI, that is a presentation feature rather than a storage change.

## Health checks

```bash
curl http://localhost:8500/health
docker-compose ps
docker-compose logs -f api
docker-compose logs -f web
docker-compose logs -f bot
```

## Troubleshooting

### Web unavailable
- inspect `docker-compose logs web`
- check `WEB_PORT`

### API unavailable
- inspect `docker-compose logs api`
- verify `API_PORT`
- confirm PostgreSQL is healthy

### Bot login/archive issues
- verify Matrix credentials
- inspect `docker-compose logs bot`

### Media download issues
- verify MinIO is healthy
- check `MINIO_ENDPOINT`, `MINIO_BUCKET`, and optional `MINIO_PUBLIC_URL`
