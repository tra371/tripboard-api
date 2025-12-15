import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from core.db import get_db
from core.models import Base


# file-based SQLite in tmp dir
tmp_db_fd, tmp_db_path = tempfile.mkstemp(suffix=".db")
TEST_DATABASE_URL = f"sqlite+pysqlite:///{tmp_db_path}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    os.close(tmp_db_fd)
    os.remove(tmp_db_path)


@pytest.fixture(scope="session")
def db_session(create_test_db):
    """Shared SQLAlchemy session for creating seed data."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(create_test_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
