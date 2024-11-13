from abc import abstractmethod, ABC
from typing import Any
from loguru import logger

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import async_session_maker
from src.repositories.company import CompanyRepository
from src.repositories.users import UsersRepository


class ABCUnitOfWork(ABC):
    session: AsyncSession

    # Repository classes
    users: UsersRepository
    company: CompanyRepository

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork(ABCUnitOfWork):
    def __init__(self) -> None:
        self.session_factory = async_session_maker

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.session_factory()
        self.users = UsersRepository(self.session)
        self.company = CompanyRepository(self.session)

        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if exc_type:
            logger.debug("Transaction failed. Rolling back.")
            await self.session.rollback()
        else:
            logger.debug("Transaction succeeded. Committing.")
            await self.session.commit()
        await self.session.close()
        logger.debug("Transaction ended.")
        await logger.complete()

        if exc:
            raise exc

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
