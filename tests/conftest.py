import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "shared"))
sys.path.insert(0, str(project_root / "shared/base_app"))
sys.path.insert(0, str(project_root / "services" / "api" / "app"))
sys.path.insert(0, str(project_root / "services" / "bot" / "app"))

# Test environment variables
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
os.environ["MINIO_ENDPOINT"] = "localhost:9000"
os.environ["MINIO_ROOT_USER"] = "test"
os.environ["MINIO_ROOT_PASSWORD"] = "test123"
os.environ["MINIO_BUCKET"] = "test-bucket"
