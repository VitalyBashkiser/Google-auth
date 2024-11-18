from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.db import Base


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=True)
    registration_date: Mapped[str] = mapped_column(String, nullable=True)
    authorized_capital: Mapped[str] = mapped_column(String, nullable=True)
    legal_form: Mapped[str] = mapped_column(String, nullable=True)
    main_activity: Mapped[str] = mapped_column(String, nullable=True)
    contact_info: Mapped[str] = mapped_column(String, nullable=True)
    authorized_person: Mapped[str] = mapped_column(String, nullable=True)
    tax_info: Mapped[str] = mapped_column(Text, nullable=True)
    registration_authorities: Mapped[str] = mapped_column(Text, nullable=True)
    last_inspection_date: Mapped[str] = mapped_column(String, nullable=True)
    company_profile: Mapped[str] = mapped_column(Text, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    subscribers = relationship("UserSubscription", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, code={self.code})>"
