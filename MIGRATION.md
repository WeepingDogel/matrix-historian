# Migration Guide: v0.1.0 → v0.2.0

This guide helps you migrate from the monolithic Matrix Historian (v0.1.0) to the new microservices architecture (v0.2.0).

## Overview of Changes

### Architecture Changes
- **Monolith → Microservices**: Bot and API now run as separate services
- **SQLite → PostgreSQL**: Centralized, scalable database
- **Frontend Removed**: Web UI removed; use API directly or build your own

### Code Changes
- **Consolidated Bot Initialization**: Removed duplicate bot initialization patterns
- **Fixed PostgreSQL Queries**: `func.date_trunc` and `func.extract` now work correctly
- **Shared Package**: Common code (models, schemas, CRUD) moved to shared package

## Migration Steps

### 1. Backup Your Data

Before migrating, backup your existing SQLite database:

```bash
# Copy your database file
cp src/app/db/database.db backup-database-$(date +%Y%m%d).db
```

### 2. Export Data from SQLite (Optional)

If you want to migrate existing data to PostgreSQL, export your tables:

```bash
# Install sqlite3 if not available
sqlite3 backup-database.db

# Export users
.mode csv
.headers on
.output users.csv
SELECT * FROM users;

# Export rooms
.output rooms.csv
SELECT * FROM rooms;

# Export messages
.output messages.csv
SELECT * FROM messages;

.quit
```

### 3. Set Up New Environment

```bash
# Clone or pull the new version
git checkout refactor/microservices-postgresql

# Create environment file
cp .env.example .env

# Edit .env with your Matrix bot credentials
nano .env
```

### 4. Start New Services

```bash
# Start all services
docker-compose up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Import Data to PostgreSQL (Optional)

If you exported data from SQLite, you can import it to PostgreSQL:

```bash
# Copy CSV files to PostgreSQL container
docker cp users.csv matrix-historian-db:/tmp/
docker cp rooms.csv matrix-historian-db:/tmp/
docker cp messages.csv matrix-historian-db:/tmp/

# Import data
docker exec -it matrix-historian-db psql -U historian -d historian -c "\copy users FROM '/tmp/users.csv' CSV HEADER;"
docker exec -it matrix-historian-db psql -U historian -d historian -c "\copy rooms FROM '/tmp/rooms.csv' CSV HEADER;"
docker exec -it matrix-historian-db psql -U historian -d historian -c "\copy messages FROM '/tmp/messages.csv' CSV HEADER;"
```

**Note**: You may need to adjust the import commands based on your table schemas. The new version automatically creates tables on startup.

### 6. Verify Migration

```bash
# Check API health
curl http://localhost:8000/health

# Check messages endpoint
curl http://localhost:8000/api/v1/messages

# View API documentation
open http://localhost:8000/docs
```

## Environment Variable Changes

| Old Variable | New Variable | Notes |
|--------------|--------------|-------|
| `DATABASE_URL` | `DATABASE_URL` | Now requires PostgreSQL connection string |
| `MATRIX_HOMESERVER` | `MATRIX_HOMESERVER` | Same |
| `MATRIX_USER` | `MATRIX_USER` | Same |
| `MATRIX_PASSWORD` | `MATRIX_PASSWORD` | Same |
| `GROQ_API_KEY` | `GROQ_API_KEY` | Same (optional) |

New default `DATABASE_URL` format:
```
postgresql://historian:historian@db:5432/historian
```

## API Changes

### Endpoints (No Breaking Changes)

All existing API endpoints remain the same:
- `GET /api/v1/messages`
- `GET /api/v1/messages/search`
- `GET /api/v1/rooms`
- `GET /api/v1/users`
- `GET /api/v1/analytics/*`

### New Endpoints

- `GET /health` - Health check endpoint for monitoring

## Troubleshooting

### "Connection refused" errors
- Ensure all services are running: `docker-compose ps`
- Check service logs: `docker-compose logs <service_name>`
- Verify database is healthy: `docker-compose exec db pg_isready`

### Data import fails
- Check CSV format matches table schema
- Ensure proper column order
- Verify data types are compatible

### Bot not receiving messages
- Check Matrix credentials in `.env`
- View bot logs: `docker-compose logs bot`
- Verify bot account has joined the rooms

### Analytics queries failing
- These now work correctly with PostgreSQL
- `func.date_trunc` and `func.extract` are PostgreSQL-native functions
- If still failing, check PostgreSQL logs

## Rollback Plan

If you need to rollback to the old version:

```bash
# Stop new services
docker-compose down

# Switch to old branch
git checkout main

# Start old services (if using Docker)
cd src
docker-compose up -d

# Or restore your backup database
cp backup-database-YYYYMMDD.db src/app/db/database.db
```

## Performance Improvements

The new architecture provides:
- **Better scalability**: Services can scale independently
- **Improved reliability**: Service isolation reduces failure impact
- **Better performance**: PostgreSQL handles concurrent access better than SQLite
- **Easier debugging**: Isolated services with independent logs

## Need Help?

- Check the [README.md](README.md) for full documentation
- View logs: `docker-compose logs -f`
- Check service status: `docker-compose ps`
- Open an issue on GitHub

---

**Note**: The frontend/webui has been permanently removed. If you need a web interface, you can:
1. Use the API directly with tools like Postman or curl
2. Build your own frontend using the REST API
3. Use the interactive API documentation at http://localhost:8000/docs
