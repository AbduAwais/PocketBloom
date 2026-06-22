"""Unit tests for password and token security helpers."""
import pytest

from src.core.config import settings
from src.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


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


def test_decode_access_token_returns_user_id():
    token = create_access_token(user_id=42)

    assert decode_access_token(token) == 42


def test_decode_access_token_rejects_malformed_token():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token("not-a-valid-token")


def test_decode_access_token_rejects_expired_token(monkeypatch):
    monkeypatch.setattr(settings, "access_token_expire_minutes", -1)
    token = create_access_token(user_id=42)

    with pytest.raises(ValueError, match="Token has expired"):
        decode_access_token(token)
