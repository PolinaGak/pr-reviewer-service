import os
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv(".env")

test_db_url = os.getenv("TEST_DATABASE_URL")

os.environ["DATABASE_URL"] = test_db_url

from app.main import app
from app.models.base import Base
from app.database import get_db

test_engine = create_engine(
    test_db_url,
    poolclass=NullPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    with test_engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS pull_requests CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS teams CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS prstatus CASCADE"))
        conn.commit()

    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
