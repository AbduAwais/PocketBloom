from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src.schemas.budget import BudgetCreate, BudgetRead


def valid_budget_data(**overrides):
    data = {
        "category_id": 1,
        "amount": Decimal("2500.00"),
        "currency": "DKK",
        "period_start": date(2026, 6, 1),
        "period_end": date(2026, 6, 30),
    }
    data.update(overrides)
    return data


def test_budget_create_normalizes_currency_and_accepts_same_day_period():
    budget = BudgetCreate(
        **valid_budget_data(
            currency=" dkk ",
            period_start=date(2026, 6, 1),
            period_end=date(2026, 6, 1),
        )
    )

    assert budget.currency == "DKK"
    assert budget.amount == Decimal("2500.00")
    assert budget.period_end == budget.period_start


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-0.01")])
def test_budget_create_rejects_non_positive_amount(amount):
    with pytest.raises(ValidationError):
        BudgetCreate(**valid_budget_data(amount=amount))


def test_budget_create_rejects_more_than_two_decimal_places():
    with pytest.raises(ValidationError):
        BudgetCreate(**valid_budget_data(amount=Decimal("10.001")))


def test_budget_create_rejects_amounts_larger_than_database_precision():
    with pytest.raises(ValidationError):
        BudgetCreate(**valid_budget_data(amount=Decimal("12345678901234567.89")))


@pytest.mark.parametrize("currency", ["DK", "DKKK", "12A"])
def test_budget_create_rejects_invalid_currency_codes(currency):
    with pytest.raises(ValidationError):
        BudgetCreate(**valid_budget_data(currency=currency))


def test_budget_create_rejects_period_ending_before_it_starts():
    with pytest.raises(ValidationError, match="period_end must be on or after"):
        BudgetCreate(
            **valid_budget_data(
                period_start=date(2026, 6, 30),
                period_end=date(2026, 6, 1),
            )
        )


def test_budget_create_rejects_non_positive_category_id():
    with pytest.raises(ValidationError):
        BudgetCreate(**valid_budget_data(category_id=0))


def test_budget_read_supports_orm_attributes():
    now = datetime.now(timezone.utc)
    db_budget = SimpleNamespace(
        id=7,
        is_active=True,
        created_at=now,
        updated_at=now,
        **valid_budget_data(),
    )

    budget = BudgetRead.model_validate(db_budget)

    assert budget.id == 7
    assert budget.category_id == 1
    assert budget.is_active is True

