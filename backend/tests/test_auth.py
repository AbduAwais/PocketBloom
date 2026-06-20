"""Integration tests for the auth endpoints (signup + login)."""
import jwt

from src.core.config import settings
from src.models.user import User


def test_signup_creates_user(client, db_session):
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "alice@example.com",
            "password": "supersecret",
            "name": "Alice",
            "phone_number": "+1234567890",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["name"] == "Alice"
    assert body["phone_number"] == "+1234567890"
    assert "id" in body
    assert "created_at" in body
    # Password must never be returned to the client.
    assert "password" not in body
    assert "hashed_password" not in body

    # Stored password is hashed, not plaintext.
    user = db_session.query(User).filter(User.email == "alice@example.com").one()
    assert user.hashed_password != "supersecret"


def test_signup_with_minimal_fields(client):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "bob@example.com", "password": "supersecret"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "bob@example.com"
    assert body["name"] is None
    assert body["phone_number"] is None


def test_signup_duplicate_email_rejected(client):
    payload = {"email": "dup@example.com", "password": "supersecret"}
    first = client.post("/api/v1/auth/signup", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/auth/signup", json=payload)
    assert second.status_code == 400
    assert second.json()["detail"] == "Email already registered"


def test_signup_invalid_email_rejected(client):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "not-an-email", "password": "supersecret"},
    )
    assert response.status_code == 422


def test_login_succeeds_with_correct_credentials(client, db_session):
    client.post(
        "/api/v1/auth/signup",
        json={"email": "carol@example.com", "password": "supersecret"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "carol@example.com", "password": "supersecret"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"

    payload = jwt.decode(
        body["access_token"],
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "iat", "exp"]},
    )
    user = db_session.query(User).filter(User.email == "carol@example.com").one()
    assert payload["sub"] == str(user.id)


def test_login_fails_with_wrong_password(client):
    client.post(
        "/api/v1/auth/signup",
        json={"email": "dave@example.com", "password": "supersecret"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "dave@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_fails_for_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@example.com", "password": "supersecret"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
