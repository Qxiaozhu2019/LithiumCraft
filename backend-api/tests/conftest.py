import os
import tempfile
from pathlib import Path

TEST_DB = Path(tempfile.gettempdir()) / "lithiumcraft-test.db"

os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB.as_posix()}")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379/15")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")

if TEST_DB.exists():
    TEST_DB.unlink()
