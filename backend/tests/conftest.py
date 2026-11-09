import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.migrations import run_migrations
import app.models  # ensure models are registered
from app.main import app

TEST_DB_FILE = "/mnt/disk230/Project/Brand Monk/backend/test_isolated.db"
test_engine = create_engine(
    f"sqlite:///{TEST_DB_FILE}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Remove previous test db if exists
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

    Base.metadata.create_all(bind=test_engine)
    run_migrations(test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass
