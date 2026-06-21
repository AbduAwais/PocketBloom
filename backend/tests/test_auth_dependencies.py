import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.core.security import create_access_token
from src.db.dependencies import get_current_user
from src.models.user import User


def bearer_credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_get_current_user_returns_token_owner(db_session):
    user = User(email="token-owner@example.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()

    current_user = get_current_user(
        bearer_credentials(create_access_token(user.id)),
        db_session,
    )

    assert current_user is user


@pytest.mark.parametrize("credentials", [None, bearer_credentials("invalid")])
def test_get_current_user_rejects_missing_or_invalid_token(
    credentials, db_session
):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials, db_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


def test_get_current_user_rejects_token_for_deleted_user(db_session):
    credentials = bearer_credentials(create_access_token(user_id=999))

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials, db_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
