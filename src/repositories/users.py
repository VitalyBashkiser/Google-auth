from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.utils.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    def __init__(self, session: AsyncSession):
        self.model = User
        super().__init__(session)
