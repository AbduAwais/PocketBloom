from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.budget import Budget
    from src.models.user import User


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        UniqueConstraint(
            "budget_id",
            "threshold_percent",
            name="uq_alerts_budget_threshold",
        ),
        CheckConstraint(
            "threshold_percent IN (20, 40, 60, 80, 100)",
            name="ck_alerts_supported_threshold",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    budget_id: Mapped[int] = mapped_column(
        ForeignKey("budgets.id", ondelete="CASCADE"),
        index=True,
    )
    threshold_percent: Mapped[int] = mapped_column(Integer)
    spent_amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2))
    message: Mapped[str] = mapped_column(Text)
    delivery_status: Mapped[str] = mapped_column(
        String,
        default="pending",
        server_default="pending",
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    user: Mapped["User"] = relationship(back_populates="alerts")
    budget: Mapped["Budget"] = relationship(back_populates="alerts")

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
