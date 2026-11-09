from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Canonical database path resolution
db_url = settings.database_url
if db_url.startswith("sqlite:///./"):
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    db_file = project_root / db_url.replace("sqlite:///./", "")
    db_url = f"sqlite:///{db_file}"

connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
