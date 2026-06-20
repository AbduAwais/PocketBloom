import pytest
from pydantic import ValidationError

from src.schemas.category import CategoryCreate, CategoryUpdate


def test_category_create_defaults_to_expense():
    category = CategoryCreate(name="Groceries")

    assert category.name == "Groceries"
    assert category.category_type == "expense"


def test_category_create_accepts_income_type():
    category = CategoryCreate(name="Salary", category_type="income")

    assert category.category_type == "income"


def test_category_create_rejects_invalid_type():
    with pytest.raises(ValidationError):
        CategoryCreate(name="Groceries", category_type="other")


@pytest.mark.parametrize("name", ["", "x" * 56])
def test_category_create_rejects_invalid_name_length(name):
    with pytest.raises(ValidationError):
        CategoryCreate(name=name)


def test_category_create_strips_name_whitespace():
    category = CategoryCreate(name="  Groceries  ")

    assert category.name == "Groceries"


def test_category_create_rejects_whitespace_only_name():
    with pytest.raises(ValidationError):
        CategoryCreate(name="   ")


def test_category_update_allows_partial_updates():
    update = CategoryUpdate(is_active=False)

    assert update.model_dump(exclude_unset=True) == {"is_active": False}


@pytest.mark.parametrize("payload", [{}, {"name": None}, {"is_active": None}])
def test_category_update_rejects_empty_or_null_updates(payload):
    with pytest.raises(ValidationError):
        CategoryUpdate(**payload)
