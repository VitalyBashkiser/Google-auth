from src.models.company import Company
from src.utils.repository import SQLAlchemyRepository


class CompanyRepository(SQLAlchemyRepository):
    """Repository class for managing Company objects in the database.

    Inherits from:
        SQLAlchemyRepository: Base repository class providing common database operations.
    """

    model = Company
