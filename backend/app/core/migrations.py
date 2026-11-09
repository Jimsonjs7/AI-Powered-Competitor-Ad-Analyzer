from sqlalchemy import text
from app.core.logging import get_logger

logger = get_logger("core.migrations")


def run_migrations(engine):
    migrations = [
        "ALTER TABLE competitors ADD COLUMN lat REAL",
        "ALTER TABLE competitors ADD COLUMN lng REAL",
        "ALTER TABLE competitors ADD COLUMN distance_km REAL",
        "ALTER TABLE competitors ADD COLUMN area VARCHAR(200)",
        "ALTER TABLE competitors ADD COLUMN ig_handle VARCHAR(100)",
        "ALTER TABLE competitors ADD COLUMN data_status VARCHAR(50) DEFAULT 'pending'",
    ]
    with engine.connect() as conn:
        for migration in migrations:
            try:
                conn.execute(text(migration))
                conn.commit()
            except Exception:
                pass  # Column already exists
    logger.info("Database schema migrations verified.")

