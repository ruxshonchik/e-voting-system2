import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app
from app.core.dependencies import get_db


@pytest.fixture()
def db_override():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client(db_override):
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def admin_client(db_override):
    with TestClient(app) as c:
        resp = c.post("/api/auth/register?role=admin", json={
            "name": "Admin User",
            "email": "admin@test.com",
            "password": "password123",
        })
        assert resp.status_code == 201, f"Admin register xatosi: {resp.text}"
        token = resp.json()["access_token"]
        c.headers.update({"Authorization": f"Bearer {token}"})
        yield c


@pytest.fixture()
def user_client(db_override):
    with TestClient(app) as c:
        resp = c.post("/api/auth/register", json={
            "name": "Regular User",
            "email": "user@test.com",
            "password": "password123",
        })
        assert resp.status_code == 201, f"User register xatosi: {resp.text}"
        token = resp.json()["access_token"]
        c.headers.update({"Authorization": f"Bearer {token}"})
        yield c
