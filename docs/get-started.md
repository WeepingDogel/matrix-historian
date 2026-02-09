# Get Started with Matrix Historian

## Quick Start Guide

Get Matrix Historian up and running in under 5 minutes using Docker Compose.

### Prerequisites

- **Docker** and **Docker Compose** installed
- At least **2GB RAM** and **10GB disk space**
- Basic familiarity with command line

### Step 1: Clone the Repository

```bash
git clone https://github.com/WeepingDogel/matrix-historian.git
cd matrix-historian
```

### Step 2: Configure Environment

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit the `.env` file with your preferred text editor. The most important settings:

```env
# Matrix Configuration
MATRIX_HOMESERVER=https://matrix.org
MATRIX_USER_ID=@your_username:matrix.org
MATRIX_ACCESS_TOKEN=your_access_token_here
MATRIX_ROOMS=!room_id:matrix.org,!another_room:matrix.org

# Database
POSTGRES_PASSWORD=secure_password_here

# MinIO Storage
MINIO_ROOT_PASSWORD=minioadmin123
```

#### Getting Matrix Access Token

1. Go to your Matrix client (Element, Cinny, etc.)
2. Go to Settings → Help & About → Access Token
3. Copy the token and paste it in `.env`

#### Finding Room IDs

1. In your Matrix client, go to the room
2. Click room name → Settings → Advanced
3. Copy the "Internal room ID"

### Step 3: Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- MinIO object storage
- Matrix Bot service
- FastAPI service

### Step 4: Verify Installation

Check if services are running:

```bash
docker-compose ps
```

You should see all 4 services with status "Up".

### Step 5: Test the API

```bash
# Check API health
curl http://localhost:8000/health

# List archived rooms
curl http://localhost:8000/api/rooms

# Get recent messages
curl http://localhost:8000/api/messages?limit=10
```

### Step 6: Access Web Interfaces

- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (login: minioadmin / minioadmin123)
- **PGAdmin** (optional): http://localhost:5050

## Basic Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MATRIX_HOMESERVER` | Matrix server URL | `https://matrix.org` |
| `MATRIX_USER_ID` | Bot user ID | Required |
| `MATRIX_ACCESS_TOKEN` | Bot access token | Required |
| `MATRIX_ROOMS` | Comma-separated room IDs | Required |
| `POSTGRES_PASSWORD` | Database password | Required |
| `MINIO_ROOT_PASSWORD` | MinIO admin password | `minioadmin123` |
| `API_HOST` | API service host | `0.0.0.0` |
| `API_PORT` | API service port | `8000` |

### Room Configuration Examples

```env
# Single room
MATRIX_ROOMS=!abc123:matrix.org

# Multiple rooms
MATRIX_ROOMS=!room1:matrix.org,!room2:matrix.org,!room3:example.com

# Community rooms
MATRIX_ROOMS=!community:matrix.org,!announcements:matrix.org
```

## First-Time Setup Walkthrough

### 1. Create Bot Account

1. Register a new account on your Matrix homeserver
2. Give it a descriptive name like "Historian Bot"
3. Save the credentials in your password manager

### 2. Invite Bot to Rooms

1. Invite the bot to each room you want to archive
2. The bot will automatically join when it starts
3. Ensure the bot has appropriate permissions (read messages)

### 3. Configure Archiving

Edit `.env` with your rooms:

```env
MATRIX_HOMESERVER=https://matrix.org
MATRIX_USER_ID=@historian-bot:matrix.org
MATRIX_ACCESS_TOKEN=syt_historianbot_abcdef123456
MATRIX_ROOMS=!general:matrix.org,!tech:matrix.org
```

### 4. Start Archiving

```bash
docker-compose up -d
docker-compose logs -f bot  # Watch the bot join rooms
```

## Common Tasks

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs bot
docker-compose logs api

# Follow logs in real-time
docker-compose logs -f bot
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes data!)
docker-compose down -v
```

### Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart bot
```

## Testing Your Setup

### Verify Bot is Working

```bash
# Check bot logs for successful connection
docker-compose logs bot | grep -i "connected\|joined\|synced"

# Send a test message in Matrix
# The bot should log receiving it
```

### Test API Endpoints

```bash
# Health check
curl -s http://localhost:8000/health | jq .

# Room list
curl -s http://localhost:8000/api/rooms | jq .

# Message count
curl -s http://localhost:8000/api/messages/count | jq .
```

### Check Storage

```bash
# Verify MinIO is accessible
curl -s http://localhost:9001/minio/health/live

# Check database connection
docker-compose exec db psql -U postgres -c "SELECT COUNT(*) FROM messages;"
```

## Next Steps

### 1. Explore the API
Visit http://localhost:8000/docs to see all available endpoints and try them out.

### 2. Configure Monitoring
Set up logging and monitoring for production use.

### 3. Backup Strategy
Configure regular backups of PostgreSQL and MinIO data.

### 4. Scale Up
Consider Kubernetes deployment for larger installations.

## Troubleshooting

### Bot Won't Connect
- Verify access token is correct
- Check homeserver URL
- Ensure bot account exists

### No Messages Archived
- Bot needs to be invited to rooms
- Check room IDs in `.env`
- Verify bot has read permissions

### API Not Responding
- Check if API service is running: `docker-compose ps api`
- View API logs: `docker-compose logs api`
- Check port 8000 is available

### Database Issues
- Check PostgreSQL logs: `docker-compose logs db`
- Verify password in `.env` matches docker-compose.yml
- Ensure sufficient disk space

## Need Help?

- Check the [Deployment Guide](./deployment.md) for detailed setup
- Review [API Reference](./reference/api-reference.md) for endpoint details
- Open an issue on GitHub for bugs or questions
- Join our Matrix room for community support

---

*You're now ready to start archiving your Matrix conversations!*