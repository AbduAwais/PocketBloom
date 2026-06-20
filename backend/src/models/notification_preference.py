from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, false, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.user import User


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    in_app_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=true(),
    )
    push_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
    )
    email_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
    )
    sms_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
    )
    alert_at_60: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=true(),
    )
    alert_at_80: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=true(),
    )
    alert_at_100: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=true(),
    )
    ai_insights_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
    )
    user: Mapped["User"] = relationship(back_populates="notification_preference")

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
