from src.models.users import User
from src.utils.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    """Repository class for managing User objects in the database.

    Inherits from:
        SQLAlchemyRepository: Base repository class providing common database operations.
    """

    model = User
