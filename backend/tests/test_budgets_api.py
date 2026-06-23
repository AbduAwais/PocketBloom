from src.core.security import create_access_token
from src.models.budget import Budget
from src.models.category import Category
from src.models.user import User


def create_user(db_session, email="owner@example.com"):
    user = User(email=email, hashed_password="hashed")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def auth_headers(user_id: int) -> dict[str, str]:
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def budget_payload(category_id: int) -> dict:
    return {
        "category_id": category_id,
        "amount": "2500.00",
        "currency": "DKK",
        "period_start": "2026-06-01",
        "period_end": "2026-06-30",
    }


def test_create_budget(client, db_session):
    user = create_user(db_session)
    category = Category(user_id=user.id, name="Groceries")
    db_session.add(category)
    db_session.commit()

    response = client.post(
        "/api/v1/budgets/",
        headers=auth_headers(user.id),
        json=budget_payload(category.id),
    )

    assert response.status_code == 201
    assert response.json()["category_id"] == category.id
    assert response.json()["amount"] == "2500.00"
    assert response.json()["currency"] == "DKK"
    assert db_session.query(Budget).count() == 1


def test_create_budget_rejects_another_users_category(client, db_session):
    owner = create_user(db_session)
    other_user = create_user(db_session, "other@example.com")
    category = Category(user_id=owner.id, name="Groceries")
    db_session.add(category)
    db_session.commit()

    response = client.post(
        "/api/v1/budgets/",
        headers=auth_headers(other_user.id),
        json=budget_payload(category.id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
    assert db_session.query(Budget).count() == 0


def test_create_duplicate_budget_returns_conflict(client, db_session):
    user = create_user(db_session)
    category = Category(user_id=user.id, name="Groceries")
    db_session.add(category)
    db_session.commit()
    url = "/api/v1/budgets/"
    headers = auth_headers(user.id)
    payload = budget_payload(category.id)

    first = client.post(url, headers=headers, json=payload)
    duplicate = client.post(url, headers=headers, json=payload)

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == (
        "A budget already exists for this category and period"
    )

