from datetime import date
from decimal import Decimal

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


def create_category(db_session, user_id: int, name="Groceries"):
    category = Category(user_id=user_id, name=name)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def create_budget_record(
    db_session,
    user_id: int,
    category_id: int,
    *,
    amount="2500.00",
    period_start=date(2026, 6, 1),
    period_end=date(2026, 6, 30),
):
    budget = Budget(
        user_id=user_id,
        category_id=category_id,
        amount=Decimal(amount),
        currency="DKK",
        period_start=period_start,
        period_end=period_end,
    )
    db_session.add(budget)
    db_session.commit()
    db_session.refresh(budget)
    return budget


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


def test_list_budgets_returns_only_current_users_budgets_in_period_order(
    client, db_session
):
    user = create_user(db_session)
    other_user = create_user(db_session, "other@example.com")
    category = create_category(db_session, user.id)
    other_category = create_category(db_session, other_user.id, "Transport")
    older = create_budget_record(
        db_session,
        user.id,
        category.id,
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 31),
    )
    newer = create_budget_record(
        db_session,
        user.id,
        category.id,
        period_start=date(2026, 6, 1),
        period_end=date(2026, 6, 30),
    )
    create_budget_record(db_session, other_user.id, other_category.id)

    response = client.get(
        "/api/v1/budgets/",
        headers=auth_headers(user.id),
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [newer.id, older.id]


def test_get_budget(client, db_session):
    user = create_user(db_session)
    category = create_category(db_session, user.id)
    budget = create_budget_record(db_session, user.id, category.id)

    response = client.get(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(user.id),
    )

    assert response.status_code == 200
    assert response.json()["id"] == budget.id
    assert response.json()["category_id"] == category.id


def test_get_unknown_budget_returns_not_found(client, db_session):
    user = create_user(db_session)

    response = client.get(
        "/api/v1/budgets/999",
        headers=auth_headers(user.id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Budget not found"


def test_user_cannot_get_another_users_budget(client, db_session):
    owner = create_user(db_session)
    other_user = create_user(db_session, "other@example.com")
    category = create_category(db_session, owner.id)
    budget = create_budget_record(db_session, owner.id, category.id)

    response = client.get(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(other_user.id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Budget not found"


def test_update_budget(client, db_session):
    user = create_user(db_session)
    category = create_category(db_session, user.id)
    budget = create_budget_record(db_session, user.id, category.id)
    payload = budget_payload(category.id)
    payload["amount"] = "3000.00"
    payload["period_end"] = "2026-07-31"

    response = client.put(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(user.id),
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["amount"] == "3000.00"
    assert response.json()["period_end"] == "2026-07-31"
    db_session.refresh(budget)
    assert budget.amount == Decimal("3000.00")


def test_update_unknown_budget_returns_not_found(client, db_session):
    user = create_user(db_session)
    category = create_category(db_session, user.id)

    response = client.put(
        "/api/v1/budgets/999",
        headers=auth_headers(user.id),
        json=budget_payload(category.id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Budget not found"


def test_user_cannot_update_another_users_budget(client, db_session):
    owner = create_user(db_session)
    other_user = create_user(db_session, "other@example.com")
    owner_category = create_category(db_session, owner.id)
    other_category = create_category(db_session, other_user.id, "Transport")
    budget = create_budget_record(db_session, owner.id, owner_category.id)

    response = client.put(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(other_user.id),
        json=budget_payload(other_category.id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Budget not found"


def test_update_budget_rejects_another_users_category(client, db_session):
    user = create_user(db_session)
    other_user = create_user(db_session, "other@example.com")
    category = create_category(db_session, user.id)
    other_category = create_category(db_session, other_user.id, "Transport")
    budget = create_budget_record(db_session, user.id, category.id)

    response = client.put(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(user.id),
        json=budget_payload(other_category.id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
    db_session.refresh(budget)
    assert budget.category_id == category.id


def test_update_duplicate_budget_returns_conflict(client, db_session):
    user = create_user(db_session)
    groceries = create_category(db_session, user.id)
    transport = create_category(db_session, user.id, "Transport")
    create_budget_record(db_session, user.id, groceries.id)
    budget = create_budget_record(
        db_session,
        user.id,
        transport.id,
        period_start=date(2026, 7, 1),
        period_end=date(2026, 7, 31),
    )

    response = client.put(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(user.id),
        json=budget_payload(groceries.id),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A budget already exists for this category and period"
    )


def test_delete_budget(client, db_session):
    user = create_user(db_session)
    category = create_category(db_session, user.id)
    budget = create_budget_record(db_session, user.id, category.id)
    budget_id = budget.id

    response = client.delete(
        f"/api/v1/budgets/{budget_id}",
        headers=auth_headers(user.id),
    )

    assert response.status_code == 204
    assert db_session.get(Budget, budget_id) is None


def test_delete_unknown_budget_returns_not_found(client, db_session):
    user = create_user(db_session)

    response = client.delete(
        "/api/v1/budgets/999",
        headers=auth_headers(user.id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Budget not found"


def test_user_cannot_delete_another_users_budget(client, db_session):
    owner = create_user(db_session)
    other_user = create_user(db_session, "other@example.com")
    category = create_category(db_session, owner.id)
    budget = create_budget_record(db_session, owner.id, category.id)

    response = client.delete(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(other_user.id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Budget not found"
    assert db_session.get(Budget, budget.id) is not None


def test_patch_budget_updates_only_supplied_fields(client, db_session):
    user = create_user(db_session)
    category = create_category(db_session, user.id)
    budget = create_budget_record(db_session, user.id, category.id)

    response = client.patch(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(user.id),
        json={"amount": "3200.00"},
    )

    assert response.status_code == 200
    assert response.json()["amount"] == "3200.00"
    assert response.json()["category_id"] == category.id
    assert response.json()["period_start"] == "2026-06-01"
    db_session.refresh(budget)
    assert budget.amount == Decimal("3200.00")


def test_patch_budget_rejects_empty_body(client, db_session):
    user = create_user(db_session)
    category = create_category(db_session, user.id)
    budget = create_budget_record(db_session, user.id, category.id)

    response = client.patch(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(user.id),
        json={},
    )

    assert response.status_code == 422


def test_patch_budget_rejects_invalid_resulting_period(client, db_session):
    user = create_user(db_session)
    category = create_category(db_session, user.id)
    budget = create_budget_record(db_session, user.id, category.id)

    response = client.patch(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(user.id),
        json={"period_start": "2026-07-01"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "period_end must be on or after period_start"
    )
    db_session.refresh(budget)
    assert budget.period_start == date(2026, 6, 1)


def test_patch_budget_rejects_another_users_category(client, db_session):
    user = create_user(db_session)
    other_user = create_user(db_session, "other@example.com")
    category = create_category(db_session, user.id)
    other_category = create_category(db_session, other_user.id, "Transport")
    budget = create_budget_record(db_session, user.id, category.id)

    response = client.patch(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(user.id),
        json={"category_id": other_category.id},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
    db_session.refresh(budget)
    assert budget.category_id == category.id


def test_user_cannot_patch_another_users_budget(client, db_session):
    owner = create_user(db_session)
    other_user = create_user(db_session, "other@example.com")
    category = create_category(db_session, owner.id)
    budget = create_budget_record(db_session, owner.id, category.id)

    response = client.patch(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(other_user.id),
        json={"amount": "1.00"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Budget not found"


def test_patch_duplicate_budget_returns_conflict(client, db_session):
    user = create_user(db_session)
    groceries = create_category(db_session, user.id)
    transport = create_category(db_session, user.id, "Transport")
    create_budget_record(db_session, user.id, groceries.id)
    budget = create_budget_record(
        db_session,
        user.id,
        transport.id,
        period_start=date(2026, 7, 1),
        period_end=date(2026, 7, 31),
    )

    response = client.patch(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers(user.id),
        json={
            "category_id": groceries.id,
            "period_start": "2026-06-01",
            "period_end": "2026-06-30",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A budget already exists for this category and period"
    )
