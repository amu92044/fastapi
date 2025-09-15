from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.config import settings
from app import models
from jose import jwt
from app.oauth2 import create_access_token  # if needed


# Create test database engine and session
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_host}:{settings.database_port}/{settings.database_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# DB session fixture for tests
@pytest.fixture()
def session():
    # Drop and recreate all tables for a clean slate before each test session
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test client with overridden dependency
@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass  # session managed by fixture

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# Fixture to create a test user and return full user data including token and id
@pytest.fixture()
def test_user(client):
    user_data = {"email": "h17223@gmail.com", "password": "password123"}

    # Create user
    res = client.post("/users/", json=user_data)
    assert res.status_code in (201, 409)  # ignore if user already exists
    created_user = res.json() if res.status_code == 201 else {"email": user_data["email"], "id": None}

    # Log in user
    login_res = client.post(
        "/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # Decode token to get user id if not created_user['id'] present
    if created_user.get("id") is None:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("user_id")
    else:
        user_id = created_user["id"]

    return {
        "email": user_data["email"],
        "password": user_data["password"],
        "token": token,
        "id": user_id,
    }


# Fixture to create a second user
@pytest.fixture()
def test_user2(client):
    user_data = {"email": "testuser2@example.com", "password": "testpass2"}

    res = client.post("/users/", json=user_data)
    assert res.status_code in (201, 409)

    login_res = client.post(
        "/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    user_id = payload.get("user_id")

    return {
        "email": user_data["email"],
        "password": user_data["password"],
        "token": token,
        "id": user_id,
    }


# Fixture to create authorized client with bearer token header
@pytest.fixture()
def authorized_client(client, test_user):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_user['token']}",
    }
    return client


# Fixture to create posts for test users
@pytest.fixture()
def test_posts(test_user, test_user2, session):
    posts_data = [
        {"title": "First Post", "content": "Content of first post", "owner_id": test_user["id"]},
        {"title": "Second Post", "content": "Content of second post", "owner_id": test_user["id"]},
        {"title": "Third Post", "content": "Content of third post", "owner_id": test_user2["id"]},
    ]

    post_models = [models.Post(**post) for post in posts_data]
    session.add_all(post_models)
    session.commit()

    return session.query(models.Post).all()
