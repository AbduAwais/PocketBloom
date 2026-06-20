"""Unit tests for password and token security helpers."""
import jwt

from src.core.config import settings
from src.core.security import create_access_token, hash_password, verify_password


def test_hash_password_is_not_plaintext():
    hashed = hash_password("supersecret")
    assert hashed != "supersecret"
    assert hashed.startswith("$2b$")  # bcrypt identifier


def test_hash_password_is_salted_and_unique():
    first = hash_password("supersecret")
    second = hash_password("supersecret")
    assert first != second  # random salt per call


def test_verify_password_accepts_correct_password():
    hashed = hash_password("supersecret")
    assert verify_password("supersecret", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("supersecret")
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_contains_user_and_expiration():
    token = create_access_token(user_id=42)

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "iat", "exp"]},
    )

    assert payload["sub"] == "42"
    assert payload["exp"] > payload["iat"]
