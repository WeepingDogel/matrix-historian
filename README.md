# Matrix Historian

A Matrix message archival and analysis tool with microservices architecture.

```mermaid
graph TB
    A[Matrix Server] -->|Events| B[Matrix Bot Service]
    B -->|Save Messages| C[PostgreSQL DB]
    B -->|Store Media| H[MinIO Storage]
    D[API Clients] -->|HTTP Requests| E[FastAPI API Service]
    E -->|Query| C
    C -->|Results| E
    E -->|Download Media| H
    E -->|Response| D
    
    F[Analysis Engine] -->|Process Data| C
    E -->|Request Analysis| F
    F -->|Analysis Results| E
    G[AI Models] -->|Sentiment/Topic Analysis| F
    
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#dfd,stroke:#333
    style E fill:#bfb,stroke:#333
    style F fill:#bff,stroke:#333
    style G fill:#fbf,stroke:#333
    style H fill:#fdb,stroke:#333
```

## Architecture

Matrix Historian now uses a **microservices architecture** with the following components:

- **Bot Service** (`services/bot/`): Connects to Matrix and archives messages to PostgreSQL, downloads and stores media files
- **API Service** (`services/api/`): FastAPI REST API for querying messages, analytics, and media
- **Shared Package** (`shared/`): Common code (models, schemas, database, CRUD operations, storage utilities)
- **PostgreSQL Database**: Centralized data storage for messages and metadata
- **MinIO Object Storage**: S3-compatible storage for media files (images, videos, audio, files)

## Features

- Automatically records Matrix room message history
- Supports message search by room, user, and content
- RESTful API for message browsing and searching
- Docker-based microservices deployment
- PostgreSQL database for scalable storage
- **Media storage with MinIO** for images, videos, audio, and files

### Media Storage Features

- **Automatic media archival**: Bot automatically downloads and stores media files from Matrix
- **MinIO object storage**: S3-compatible storage for efficient media management
- **Media metadata tracking**: Store filename, MIME type, file size, and image dimensions
- **RESTful media API**: Query media by room, user, or type
- **Presigned URLs**: Secure temporary download links for media files
- **Media statistics**: Track total media count, size, and breakdown by type
- **Filtered queries**: Search media by MIME type (e.g., images only)

### Data Analysis Features

- **Activity Overview**: Displays message trends and user activity levels
- **Word Cloud Analysis**: Generates statistics and visualizations of word frequency in chats
- **User Interaction**: Shows the network and intensity of interactions between users
- **Topic Analysis**: Tracks the evolution of topics over time
- **Sentiment Analysis**: AI-based analysis of message sentiment tendencies (requires GROQ_API_KEY)
- **Activity Analysis**: Displays heatmaps of group activity during different times

All analysis features support filtering by time range and room.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- A Matrix account for the bot
- (Optional) GROQ API key for AI analysis features

### Deploy with Docker Compose

1. Clone the repository
```bash
git clone https://github.com/EnsueCollectR/matrix-historian.git
cd matrix-historian
```

2. Configure environment variables
```bash
cp .env.example .env
# Edit .env file to set Matrix bot credentials and other configuration
```

Required environment variables:
- `MATRIX_HOMESERVER`: Your Matrix homeserver URL (e.g., https://matrix.org)
- `MATRIX_USER`: Bot username (e.g., @yourbot:matrix.org)
- `MATRIX_PASSWORD`: Bot password
- `GROQ_API_KEY`: (Optional) For AI sentiment analysis

3. Start the services
```bash
docker-compose up -d
```

4. Check service status
```bash
docker-compose ps
docker-compose logs -f
```

Services will start on the following ports:
- **API service**: http://localhost:8500 (configurable via `API_PORT`)
- **API documentation**: http://localhost:8500/docs (Swagger UI)
- **MinIO Console**: http://localhost:9001 (web UI for managing media storage)
- **MinIO API**: http://localhost:9000 (S3-compatible API endpoint)

### Database Migration

The application automatically creates database tables on startup. For production deployments, consider using Alembic for migrations (see Development section).

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MATRIX_HOMESERVER` | Matrix server address | - | Yes |
| `MATRIX_USER` | Bot username | - | Yes |
| `MATRIX_PASSWORD` | Bot password | - | Yes |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://historian:historian@db:5432/historian` | No |
| `MINIO_ROOT_USER` | MinIO admin username | `historian` | No |
| `MINIO_ROOT_PASSWORD` | MinIO admin password | `historian123` | No |
| `MINIO_ENDPOINT` | MinIO endpoint | `minio:9000` | No |
| `MINIO_BUCKET` | MinIO bucket name | `matrix-media` | No |
| `MINIO_API_PORT` | MinIO API port | `9000` | No |
| `MINIO_CONSOLE_PORT` | MinIO console port | `9001` | No |
| `API_PORT` | API service port | `8500` | No |
| `GROQ_API_KEY` | API key for AI analysis | - | No |

## Media Storage with MinIO

Matrix Historian uses MinIO for storing media files uploaded to Matrix rooms. MinIO is an S3-compatible object storage system that runs as a Docker container.

### Accessing MinIO Console

The MinIO web console is available at http://localhost:9001

**Default credentials:**
- Username: `historian`
- Password: `historian123`

From the console, you can:
- Browse stored media files
- Monitor storage usage
- Manage buckets and policies
- View access logs

### How Media Storage Works

1. **Bot receives media event** from Matrix (image, video, audio, or file)
2. **Bot downloads media** from the Matrix server using the `mxc://` URL
3. **Bot uploads to MinIO** with a unique UUID-based key
4. **Metadata saved to PostgreSQL** including filename, MIME type, size, dimensions
5. **API provides download URLs** via presigned URLs that expire after 1 hour

### Supported Media Types

- **Images**: `m.image` (JPEG, PNG, GIF, WebP, etc.)
- **Videos**: `m.video` (MP4, WebM, etc.)
- **Audio**: `m.audio` (MP3, OGG, etc.)
- **Files**: `m.file` (any file type)

### Storage Organization

Media files are stored in MinIO with the following structure:
```
matrix-media/  (bucket)
├── <uuid>/
│   └── original_filename.ext
```

Each file is stored under a unique UUID path to prevent naming conflicts.

## API Usage

The API service provides RESTful endpoints for querying messages, analytics, and media.

**Base URL**: http://localhost:8500/api/v1

**Interactive Documentation**: http://localhost:8500/docs

### Example Endpoints

#### Messages
- `GET /api/v1/messages` - List messages with pagination
- `GET /api/v1/messages/search` - Search messages by content
- `GET /api/v1/rooms` - List rooms
- `GET /api/v1/users` - List users

#### Analytics
- `GET /api/v1/analytics/overview` - Get analytics overview
- `GET /api/v1/analytics/trends` - Get message trends
- `GET /api/v1/analytics/activity-heatmap` - Get activity heatmap

#### Media
- `GET /api/v1/media/` - List all media with pagination
- `GET /api/v1/media/stats` - Get media statistics (count, size, by type)
- `GET /api/v1/media/room/{room_id}` - List media in a specific room
- `GET /api/v1/media/user/{user_id}` - List media sent by a specific user
- `GET /api/v1/media/{media_id}` - Get media metadata with download URL
- `GET /api/v1/media/{media_id}/download` - Download media file

**Media query parameters:**
- `skip` - Pagination offset
- `limit` - Number of results (default: 100)
- `mime_type` - Filter by MIME type prefix (e.g., `image/` for images only)

See the [API documentation](http://localhost:8500/docs) for complete endpoint details.

## Development

### Project Structure

```
matrix-historian/
├── docker-compose.yml          # Multi-service orchestration
├── .env.example                # Environment variables template
├── shared/                     # Shared code package
│   ├── app/
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── crud/              # Database operations
│   │   ├── storage/           # Storage utilities (MinIO client)
│   │   ├── db/                # Database configuration
│   │   └── utils/             # Utility functions
│   └── setup.py
├── services/
│   ├── bot/                   # Matrix bot service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       ├── main.py
│   │       └── bot.py
│   └── api/                   # FastAPI service
│       ├── Dockerfile
│       ├── requirements.txt
│       └── app/
│           ├── main.py
│           ├── api/           # API routes (messages, analytics, media)
│           └── ai/            # AI analysis
└── docs/                      # Documentation
```

### Local Development Setup

For local development without Docker:

1. **Install PostgreSQL**
```bash
# On Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE historian;
CREATE USER historian WITH PASSWORD 'historian';
GRANT ALL PRIVILEGES ON DATABASE historian TO historian;
```

2. **Install Python dependencies**
```bash
# Install shared package
cd shared
pip install -e .

# Install bot service dependencies
cd ../services/bot
pip install -r requirements.txt

# Install API service dependencies
cd ../services/api
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export DATABASE_URL="postgresql://historian:historian@localhost:5432/historian"
export MATRIX_HOMESERVER="https://matrix.org"
export MATRIX_USER="@yourbot:matrix.org"
export MATRIX_PASSWORD="your_password"
```

4. **Run services**
```bash
# Terminal 1: Run bot service
cd services/bot/app
python main.py

# Terminal 2: Run API service
cd services/api/app
uvicorn main:app --reload --port 8000
```

### Database Migrations with Alembic (Optional)

For production deployments, use Alembic for database migrations:

```bash
# Install Alembic
pip install alembic

# Initialize Alembic in shared package
cd shared
alembic init alembic

# Edit alembic.ini and set sqlalchemy.url
# Edit alembic/env.py to import Base from app.db.database

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Testing

```bash
# Run tests
cd tests
pytest
```

## Migration from Previous Version

This version represents a significant architectural change from the monolithic application:

- **SQLite → PostgreSQL**: All data must be migrated to PostgreSQL
- **Monolith → Microservices**: Bot and API now run as separate services
- **Frontend Removed**: The web UI has been removed; use the API directly or build your own frontend

### Breaking Changes

- Database format changed from SQLite to PostgreSQL
- Configuration now uses environment variables exclusively
- Bot and API run as separate processes
- `func.date_trunc` and `func.extract` queries now work correctly with PostgreSQL

## Troubleshooting

### Bot not connecting to Matrix
- Check `MATRIX_HOMESERVER`, `MATRIX_USER`, and `MATRIX_PASSWORD` in `.env`
- View bot logs: `docker-compose logs bot`

### API service not starting
- Ensure PostgreSQL is healthy: `docker-compose ps db`
- Check API logs: `docker-compose logs api`

### Database connection errors
- Verify `DATABASE_URL` is correct
- Ensure the `db` service is running and healthy
- Check PostgreSQL logs: `docker-compose logs db`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 0.3.0 (Media Storage)

- ✨ **MinIO object storage integration** for media files
- ✨ **Automatic media archival** from Matrix (images, videos, audio, files)
- ✨ **Media API endpoints** for querying and downloading media
- ✨ **Media metadata tracking** (filename, MIME type, size, dimensions)
- ✨ **Presigned download URLs** for secure media access
- ✨ **Media statistics** and filtering by type
- 🔧 Enhanced bot to handle media events
- 🔧 MinIO health checks and dependencies in docker-compose
- 📝 Updated documentation with media storage guide

### Version 0.2.0 (Microservices Refactor)

- ✨ Migrated to microservices architecture
- ✨ PostgreSQL database support (replaces SQLite)
- ✨ Separate bot and API services
- ✨ Shared package for common code
- ✨ Docker Compose orchestration
- ✨ Fixed `func.date_trunc` PostgreSQL compatibility issues
- ✨ Consolidated bot initialization (removed duplicate patterns)
- 🔧 Improved error handling and logging
- 🔧 Health checks for all services
- 📝 Updated documentation

### Version 0.1.0 (Legacy Monolith)

- Initial monolithic application
- SQLite database
- Combined bot + API in single process

---

[中文文档](README_zh.md) (Note: Chinese documentation may be outdated)
