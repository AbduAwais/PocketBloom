from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.bank_connection import BankConnection


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    bank_connection_id: Mapped[int] = mapped_column(
        ForeignKey("bank_connections.id", ondelete="CASCADE"),
        index=True,
    )
    provider_account_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    iban: Mapped[str | None] = mapped_column(String, nullable=True)
    currency: Mapped[str] = mapped_column(String)
    account_type: Mapped[str | None] = mapped_column(String, nullable=True)
    bank_connection: Mapped["BankConnection"] = relationship(
        back_populates="bank_accounts"
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
