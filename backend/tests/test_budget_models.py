from datetime import date
from decimal import Decimal

from src.models import (
    Alert,
    BankAccount,
    BankConnection,
    Budget,
    Category,
    NotificationPreference,
    Transaction,
    User,
)


def test_budgeting_model_relationships(db_session):
    user = User(email="budget@example.com", hashed_password="hashed")
    category = Category(name="Groceries", user=user)
    budget = Budget(
        user=user,
        category=category,
        amount=Decimal("3000.00"),
        period_start=date(2026, 6, 1),
        period_end=date(2026, 6, 30),
    )
    alert = Alert(
        user=user,
        budget=budget,
        threshold_percent=60,
        spent_amount=Decimal("1800.00"),
        message="You have used 60% of your groceries budget.",
    )
    preference = NotificationPreference(user=user)
    connection = BankConnection(
        user=user,
        institution_id="NORDEA_NDEADKKK",
        requisition_id="requisition-1",
    )
    account = BankAccount(
        bank_connection=connection,
        provider_account_id="account-1",
        currency="DKK",
    )
    transaction = Transaction(
        bank_account=account,
        category=category,
        provider_transaction_id="transaction-1",
        amount=Decimal("-125.50"),
        currency="DKK",
        booking_date=date(2026, 6, 20),
        status="booked",
    )

    db_session.add(user)
    db_session.commit()

    assert transaction.category is category
    assert category.transactions == [transaction]
    assert category.budgets == [budget]
    assert budget.alerts == [alert]
    assert user.notification_preference is preference
    assert preference.in_app_enabled is True
    assert preference.push_enabled is False
    assert preference.ai_insights_enabled is False
