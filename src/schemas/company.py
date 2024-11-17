from datetime import datetime

from pydantic import BaseModel


class CompanyDataModel(BaseModel):
    id: int | None = None
    name: str | None
    code: str
    status: str | None
    registration_date: str | None
    authorized_capital: str | None
    legal_form: str | None
    main_activity: str | None
    contact_info: str | None
    authorized_person: str | None
    tax_info: str | None
    registration_authorities: str | None
    last_inspection_date: str | None
    company_profile: str | None
    last_updated: datetime = datetime.utcnow()

    class Config:
        """
        Configuration class to enable ORM mode and attribute access.
        """

        from_attributes = True
