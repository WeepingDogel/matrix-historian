# Matrix Historian - Development Guide

## Development Environment Setup

### Prerequisites

- **Python 3.9+** (3.12 recommended)
- **Docker & Docker Compose** (for local services)
- **Git** for version control
- **UV** for dependency management (recommended)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/WeepingDogel/matrix-historian.git
cd matrix-historian

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install UV (recommended package manager)
pip install uv

# Or install traditional pip requirements
pip install -r requirements.txt
```

### Step 2: Start Development Services

```bash
# Start database and storage services
docker-compose up -d db minio

# Or start all services for full development
docker-compose up -d
```

### Step 3: Install Development Dependencies

```bash
# Install all dependencies with UV
uv sync --dev

# Or install specific development packages
pip install pytest pytest-cov black isort mypy pre-commit
```

## Project Structure

```
matrix-historian/
├── services/                    # Microservices
│   ├── api/                    # FastAPI REST API
│   │   ├── app/
│   │   │   ├── api/           # API endpoints
│   │   │   ├── core/          # Core configurations
│   │   │   ├── models/        # Database models
│   │   │   ├── schemas/       # Pydantic schemas
│   │   │   └── services/      # Business logic
│   │   ├── tests/             # API tests
│   │   └── main.py            # API entry point
│   ├── bot/                    # Matrix bot service
│   │   ├── handlers/          # Message handlers
│   │   ├── services/          # Bot services
│   │   └── main.py            # Bot entry point
│   └── shared/                 # Shared code
│       ├── database/          # Database utilities
│       ├── models/            # Shared models
│       ├── schemas/           # Shared schemas
│       └── storage/           # Storage utilities
├── docs/                       # Documentation
├── tests/                      # Integration tests
├── docker-compose.yml          # Docker Compose configuration
├── .env.example               # Environment template
└── pyproject.toml             # Project configuration
```

## Development Workflow

### 1. Running Services Locally

#### API Service Development

```bash
cd services/api

# Run with auto-reload for development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the development script
python -m app.main
```

#### Bot Service Development

```bash
cd services/bot

# Run bot in development mode
python main.py --dev

# With debug logging
python main.py --debug
```

#### Running All Services

```bash
# Using Docker Compose for development
docker-compose -f docker-compose.dev.yml up

# Or run each service in separate terminals
```

### 2. Code Quality Tools

#### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

#### Code Formatting

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check types with mypy
mypy .
```

#### Linting

```bash
# Run flake8
flake8 .

# Run pylint
pylint services/
```

### 3. Testing

#### Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=services --cov-report=html

# Run tests in watch mode (requires pytest-watch)
ptw
```

#### Integration Tests

```bash
# Start test services
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/

# Clean up test services
docker-compose -f docker-compose.test.yml down -v
```

#### API Testing

```bash
# Using curl
curl http://localhost:8000/health

# Using httpie
http :8000/health

# Using the API documentation
# Visit http://localhost:8000/docs
```

## Development Practices

### 1. Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/your-feature-name

# Create pull request
gh pr create --title "Add new feature" --body "Description of changes"
```

### 2. Commit Message Convention

Follow Conventional Commits:

```
feat: add new endpoint for message search
fix: resolve database connection issue
docs: update API documentation
style: format code with black
refactor: reorganize service structure
test: add unit tests for bot service
chore: update dependencies
```

### 3. Environment Configuration

Create `.env.development` for local development:

```env
# Development-specific settings
DEBUG=true
LOG_LEVEL=DEBUG

# Use local services
DATABASE_URL=postgresql://postgres:password@localhost:5432/matrix_historian_dev
MINIO_ENDPOINT=localhost:9000

# Test Matrix credentials
MATRIX_HOMESERVER=https://matrix.org
MATRIX_USER_ID=@testbot:matrix.org
MATRIX_ACCESS_TOKEN=test_token
MATRIX_ROOMS=!testroom:matrix.org
```

### 4. Database Migrations

```bash
# Generate new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check migration status
alembic current
```

## API Development

### Adding New Endpoints

1. Create route file in `services/api/app/api/v1/`:

```python
# services/api/app/api/v1/your_endpoint.py
from fastapi import APIRouter, Depends
from app.schemas.your_schema import YourSchema
from app.services.your_service import YourService

router = APIRouter(prefix="/your-endpoint", tags=["your-tag"])

@router.get("/", response_model=list[YourSchema])
async def get_items(
    service: YourService = Depends(),
    skip: int = 0,
    limit: int = 100
):
    return await service.get_items(skip=skip, limit=limit)
```

2. Add router to `services/api/app/api/v1/__init__.py`:

```python
from . import your_endpoint

__all__ = ["your_endpoint"]
```

3. Register in `services/api/app/api/__init__.py`:

```python
api_router.include_router(your_endpoint.router)
```

### Adding Database Models

1. Create model in `services/shared/models/`:

```python
# services/shared/models/your_model.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base

class YourModel(Base):
    __tablename__ = "your_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

2. Create Pydantic schemas in `services/shared/schemas/`:

```python
# services/shared/schemas/your_schema.py
from pydantic import BaseModel
from datetime import datetime

class YourSchemaBase(BaseModel):
    name: str

class YourSchemaCreate(YourSchemaBase):
    pass

class YourSchema(YourSchemaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## Bot Service Development

### Adding Message Handlers

1. Create handler in `services/bot/handlers/`:

```python
# services/bot/handlers/your_handler.py
from nio import RoomMessageText
import logging

logger = logging.getLogger(__name__)

async def handle_your_event(room, event):
    """Handle specific type of Matrix event."""
    if isinstance(event, RoomMessageText):
        message = event.body
        logger.info(f"Received message: {message}")
        
        # Your handler logic here
        if "hello" in message.lower():
            await room.send_text("Hello there!")
```

2. Register handler in `services/bot/main.py`:

```python
from handlers.your_handler import handle_your_event

# Add to event handlers
client.add_event_callback(handle_your_event, RoomMessageText)
```

### Testing Bot Handlers

```python
# tests/test_bot_handlers.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from bot.handlers.your_handler import handle_your_event

@pytest.mark.asyncio
async def test_handle_your_event():
    # Mock room and event
    room = AsyncMock()
    event = MagicMock()
    event.body = "Hello world"
    
    # Test handler
    await handle_your_event(room, event)
    
    # Verify behavior
    room.send_text.assert_called_once_with("Hello there!")
```

## Shared Code Development

### Adding Shared Utilities

1. Create utility in `services/shared/`:

```python
# services/shared/utils/your_util.py
import logging
from typing import Any

logger = logging.getLogger(__name__)

def your_utility_function(data: Any) -> Any:
    """Document your utility function."""
    logger.debug(f"Processing data: {data}")
    # Your utility logic
    return processed_data
```

2. Update `services/shared/__init__.py`:

```python
from .utils.your_util import your_utility_function

__all__ = ["your_utility_function"]
```

## Debugging

### Common Debugging Techniques

#### Logging Configuration

```python
# Add to your code
import logging
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

#### Debugging API Endpoints

```bash
# Enable debug mode
DEBUG=true uvicorn main:app --reload

# Use curl with verbose output
curl -v http://localhost:8000/your-endpoint

# Use Python debugger
import pdb; pdb.set_trace()
```

#### Debugging Bot Service

```bash
# Run with debug logging
python main.py --log-level DEBUG

# Enable Matrix SDK debugging
import nio
nio.log.logger.setLevel(logging.DEBUG)
```

### Using Docker for Debugging

```bash
# Access running container
docker-compose exec api bash

# View logs in real-time
docker-compose logs -f api

# Check container resources
docker stats

# Inspect container
docker inspect matrix-historian-api
```

## Performance Optimization

### Database Optimization

```python
# Use eager loading for relationships
query = session.query(Message).options(
    joinedload(Message.sender),
    joinedload(Message.room)
)

# Add indexes for frequent queries
# In your model:
__table_args__ = (
    Index('idx_message_room_date', 'room_id', 'timestamp'),
    Index('idx_message_sender', 'sender_id'),
)
```

### API Optimization

```python
# Implement caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@router.get("/messages")
@cache(expire=60)  # Cache for 60 seconds
async def get_messages():
    return await message_service.get_all()
```

### Bot Optimization

```python
# Batch message processing
async def process_messages_batch(messages: list):
    # Process multiple messages at once
    await database.bulk_insert(messages)
    
# Use connection pooling
from nio import AsyncClient
client = AsyncClient(
    homeserver,
    user_id,
    device_id="historian_bot",
    store_path="./matrix_store",
    config=ClientConfig(store_sync_tokens=True)
)
```

## Testing Strategy

### Test Pyramid

```
        /\
       /  \      E2E Tests (10%)
      /    \
     /______\    Integration Tests (20%)
    /        \
   /__________\  Unit Tests (70%)
```

### Writing Tests

#### Unit Tests

```python
# tests/unit/test_your_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.your_service import YourService

class TestYourService:
    @pytest.fixture
    def service(self):
        return YourService(Mock())
    
    def test_something(self, service):
        # Arrange
        service.repository.get.return_value = expected
        
        # Act
        result = service.get_something(1)
        
        # Assert
        assert result == expected
```

#### Integration Tests

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_messages(client):
    response = client.get("/api/v1/messages")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

#### E2E Tests

```python
# tests/e2e/test_full_flow.py
import pytest
import docker
from matrix_client import MatrixClient

@pytest.fixture(scope="module")
def docker_services():
    # Start all services
    client = docker.from_env()
    containers = client.containers.run(
        "matrix-historian:test",
        detach=True,
        ports={'8000/tcp': 8000}
    )
    yield containers
    containers.stop()
```

## Documentation

### Code Documentation

```python
def process_message(message: str, options: dict = None) -> dict:
    """
    Process a Matrix message with given options.
    
    Args:
        message: The message text to process
        options: Optional processing options
        
    Returns:
        dict: Processed message data
        
    Raises:
        ValueError: If message is empty
        
    Examples:
        >>> process_message("Hello", {"lang": "en"})
        {'text': 'Hello', 'language': 'en'}
    """
    if not message:
        raise ValueError("Message cannot be empty")
    
    # Implementation
    return {"text": message, "language": options.get("lang") if options else None}
```

### API Documentation

```python
from fastapi import Query
from typing import Optional

@router.get("/search")
async def search_messages(
    q: str = Query(..., description="Search query"),
    room_id: Optional[str] = Query(None, description="Filter by room ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results")
):
    """
    Search messages across all archived rooms.
    
    This endpoint allows full-text search of archived messages with
    optional filtering by room.
    
    Returns up to 1000 messages matching the search criteria.
    """
    return await search_service.search(q, room_id, limit)
```

## Deployment Preparation

### Building for Production

```bash
# Build Docker images
docker build -t matrix-historian-api:latest -f services/api/Dockerfile .
docker build -t matrix-historian-bot:latest -f services/bot/Dockerfile .

# Run security scan
trivy image matrix-historian-api:latest

# Run vulnerability scan
snyk test --docker matrix-historian-api:latest
```

### Creating Release

```bash
# Update version
bump2version patch  # or minor/major

# Create release notes
git log --oneline $(git describe --tags --abbrev=0)..HEAD

# Tag release
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3

# Create GitHub release
gh release create v1.2.3 --notes-file CHANGELOG.md
```

## Contributing Guidelines

### Before Submitting PR

1. Run tests: `pytest`
2. Check formatting: `black --check .`
3. Run linters: `flake8 .`
4. Update documentation
5. Add/update tests for new features

### Code Review Checklist

- [ ] Code follows project style guide
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Backward compatibility maintained

### Getting Help

- Check existing issues on GitHub
- Join Matrix room for development discussions
- Review existing code examples
- Ask for code review early

---

*Happy coding! Remember to write tests and document your work.*