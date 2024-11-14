from sqlalchemy import Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.db.db import Base


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[id] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="subscriptions")
    company = relationship("Company", back_populates="subscribers")
