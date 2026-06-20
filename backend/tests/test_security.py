"""Unit tests for password hashing helpers."""
from src.core.security import hash_password, verify_password


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
