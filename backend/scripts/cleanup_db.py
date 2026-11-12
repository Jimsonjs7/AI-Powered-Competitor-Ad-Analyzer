"""Database cleanup and re-initialization script for BrandMonk Ad Desk.

Usage:
    uv run --project backend python backend/scripts/cleanup_db.py
    uv run --project backend python backend/scripts/cleanup_db.py --keep-media
"""

import argparse
import shutil
import sys
from pathlib import Path

# Ensure backend directory is on sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.core.database import Base, engine
from app.core.migrations import run_migrations
import app.models  # noqa: F401 - register all SQLAlchemy models


def cleanup_database(clear_media: bool = True) -> None:
    """Drop all database tables, remove stale SQLite files, and rebuild clean schema."""
    print("Disposing active SQLAlchemy engine connections...")
    engine.dispose()

    # Remove SQLite database files if using SQLite
    if settings.database_url.startswith("sqlite"):
        db_files = [
            PROJECT_ROOT / "brandmonk.db",
            PROJECT_ROOT / "brandmonk.db-wal",
            PROJECT_ROOT / "brandmonk.db-shm",
            BACKEND_DIR / "brandmonk.db",
            BACKEND_DIR / "brandmonk.db-wal",
            BACKEND_DIR / "brandmonk.db-shm",
        ]
        for db_file in db_files:
            if db_file.exists():
                db_file.unlink()
                print(f"  Removed stale database file: {db_file}")
    else:
        print("Dropping all tables in configured database...")
        Base.metadata.drop_all(bind=engine)

    # Clear cached media creatives and generated posters if requested
    if clear_media:
        media_dir = Path(settings.media_storage_dir)
        if not media_dir.is_absolute():
            media_dir = PROJECT_ROOT / media_dir
        for sub in ("creatives", "posters"):
            target = media_dir / sub
            if target.exists():
                shutil.rmtree(target)
                print(f"  Cleared media cache directory: {target}")
            target.mkdir(parents=True, exist_ok=True)

    # Recreate clean schema & run migrations
    print("Creating fresh database schema...")
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)
    print("Database cleanup complete. System is ready at a clean state (Step 1).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean and re-initialize the BrandMonk Ad Desk database.")
    parser.add_argument(
        "--keep-media",
        action="store_true",
        help="Keep cached images and posters in media_storage/ instead of clearing them.",
    )
    args = parser.parse_args()
    cleanup_database(clear_media=not args.keep_media)

