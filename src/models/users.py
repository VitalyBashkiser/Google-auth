from sqlalchemy import Integer, String, Boolean, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser = mapped_column(Boolean, default=False)
    permissions = mapped_column(ARRAY(String), default=[], server_default="{}")
    subscriptions = relationship("UserSubscription", back_populates="user")
