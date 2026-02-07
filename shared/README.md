# Shared Package

This package contains shared code used by all Matrix Historian microservices.

## Contents

- **models/**: SQLAlchemy database models
- **schemas/**: Pydantic schemas for data validation
- **crud/**: Database CRUD operations
- **db/**: Database configuration and connection
- **utils/**: Utility functions

## Installation

```bash
pip install -e .
```

## Database Migrations with Alembic

This package includes Alembic for database schema migrations.

### Initialize Database

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://historian:historian@localhost:5432/historian"

# Create initial migration
cd shared
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Create New Migration

```bash
# After modifying models
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/

# Apply migration
alembic upgrade head
```

### Migration Commands

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>
```

## Usage in Services

Services should add `/app/shared` to their Python path:

```python
import sys
sys.path.insert(0, '/app/shared')

from app.db.database import get_db, init_db
from app.models.message import User, Room, Message
from app.crud import message as crud
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .
```
