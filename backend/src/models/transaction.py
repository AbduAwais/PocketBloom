from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.bank_account import BankAccount


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint(
            "bank_account_id",
            "provider_transaction_id",
            name="uq_transactions_account_provider_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    bank_account_id: Mapped[int] = mapped_column(
        ForeignKey("bank_accounts.id", ondelete="CASCADE"),
        index=True,
    )
    provider_transaction_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2))
    currency: Mapped[str] = mapped_column(String(3))
    booking_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    value_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    creditor_name: Mapped[str | None] = mapped_column(String, nullable=True)
    debtor_name: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String)
    bank_account: Mapped["BankAccount"] = relationship(
        back_populates="transactions"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
