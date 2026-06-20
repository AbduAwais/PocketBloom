from src.models.category import Category
from src.models.user import User


def create_user(db_session, email="owner@example.com"):
    user = User(email=email, hashed_password="hashed")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_create_category(client, db_session):
    user = create_user(db_session)

    response = client.post(
        f"/api/v1/categories/?user_id={user.id}",
        json={"name": "Groceries"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Groceries"
    assert response.json()["category_type"] == "expense"


def test_create_category_rejects_unknown_user(client):
    response = client.post(
        "/api/v1/categories/?user_id=999",
        json={"name": "Groceries"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_duplicate_category_returns_conflict_and_rolls_back(
    client, db_session
):
    user = create_user(db_session)
    url = f"/api/v1/categories/?user_id={user.id}"

    assert client.post(url, json={"name": "Groceries"}).status_code == 201
    duplicate = client.post(url, json={"name": "Groceries"})
    after_rollback = client.post(url, json={"name": "Transport"})

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == (
        "A category with this name already exists"
    )
    assert after_rollback.status_code == 201


def test_update_category_rejects_empty_body(client, db_session):
    user = create_user(db_session)
    category = Category(user_id=user.id, name="Groceries")
    db_session.add(category)
    db_session.commit()

    response = client.patch(
        f"/api/v1/categories/{category.id}?user_id={user.id}",
        json={},
    )

    assert response.status_code == 422


def test_user_cannot_update_another_users_category(client, db_session):
    owner = create_user(db_session)
    other_user = create_user(db_session, "other@example.com")
    category = Category(user_id=owner.id, name="Groceries")
    db_session.add(category)
    db_session.commit()

    response = client.patch(
        f"/api/v1/categories/{category.id}?user_id={other_user.id}",
        json={"name": "Changed"},
    )

    assert response.status_code == 404
    assert category.name == "Groceries"


def test_delete_category(client, db_session):
    user = create_user(db_session)
    category = Category(user_id=user.id, name="Groceries")
    db_session.add(category)
    db_session.commit()

    response = client.delete(
        f"/api/v1/categories/{category.id}?user_id={user.id}"
    )

    assert response.status_code == 204
    assert db_session.get(Category, category.id) is None
