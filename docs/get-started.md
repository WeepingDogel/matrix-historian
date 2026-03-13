# Get Started

This guide reflects the current Docker Compose setup in the repository.

## Prerequisites

- Docker
- Docker Compose
- a Matrix account for the bot

## 1. Clone the repository

```bash
git clone https://github.com/WeepingDogel/matrix-historian.git
cd matrix-historian
```

## 2. Create `.env`

```bash
cp .env.example .env
```

Minimum useful settings:

```env
MATRIX_HOMESERVER=https://matrix.org
MATRIX_USER=@yourbot:matrix.org
MATRIX_PASSWORD=your_bot_password
DATABASE_URL=postgresql://historian:historian@db:5432/historian
API_PORT=8500
WEB_PORT=3000
MINIO_ROOT_USER=historian
MINIO_ROOT_PASSWORD=historian123
MINIO_ENDPOINT=minio:9000
MINIO_BUCKET=matrix-media
```

Optional:

```env
MINIO_PUBLIC_URL=https://your-public-minio.example
GROQ_API_KEY=your_groq_api_key_here
```

## 3. Start all services

```bash
docker-compose up -d
```

The default stack includes:
- `db`
- `minio`
- `bot`
- `api`
- `web`

## 4. Verify service status

```bash
docker-compose ps
docker-compose logs -f
```

## 5. Open the app

- Web UI: http://localhost:3000
- API: http://localhost:8500
- Swagger docs: http://localhost:8500/docs
- MinIO Console: http://localhost:9001

## 6. Verify API health

```bash
curl http://localhost:8500/health
```

## Frontend behavior

### Languages

The web frontend currently supports:
- English (`en`)
- Simplified Chinese (`zh-CN`)

### Time display

The API/backend stores timestamps in UTC.

The frontend can present those timestamps in:
- **Local**: browser timezone
- **UTC**

This is expected behavior and does not require DB/backend modification.

## Common commands

```bash
# stop services
docker-compose down

# rebuild and start
docker-compose up -d --build

# watch logs
docker-compose logs -f api
docker-compose logs -f web
docker-compose logs -f bot
```

## Common issues

### Web UI does not load
- check `docker-compose ps`
- inspect `docker-compose logs web`
- confirm port `3000` is free

### API does not respond
- inspect `docker-compose logs api`
- confirm port `8500` is free
- verify `db` is healthy

### Bot does not archive messages
- verify `MATRIX_HOMESERVER`, `MATRIX_USER`, `MATRIX_PASSWORD`
- confirm the bot account can log in and join the target rooms
- inspect `docker-compose logs bot`
