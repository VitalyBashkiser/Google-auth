from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar, List

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger
from src.models.user_subscription import UserSubscription
from src.models.users import User


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, user_id: int, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def update_instance(self, instance, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, user_id: int):
        raise NotImplementedError

    async def find_one(self, **filter_by):
        raise NotImplementedError

    async def get_stale_records(self, threshold: datetime):
        raise NotImplementedError


ModelType = TypeVar("ModelType")


class SQLAlchemyRepository(AbstractRepository):
    """
    Base repository class providing common CRUD operations.

    Attributes:
        model: The model class associated with this repository.
        session (AsyncSession): The database session to use for operations.
    """
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict):
        """
        Adds a new record to the database.

        Args:
            data (dict): The data to insert.

        Returns:
            The created model instance.
        """
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def update_one(self, record_id: int, data: dict) -> int:
        """
        Updates a single record identified by its ID.

        Args:
            record_id (int): The ID of the record to update.
            data (dict): The updated data.

        Returns:
            int: The ID of the updated record.
        """
        stmt = update(self.model).values(**data).filter_by(id=record_id).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def update_instance(self, instance, data: dict) -> None:
        """
        Updates an instance in place using provided data.

        Args:
            instance: The model instance to update.
            data (dict): The data to set on the instance.

        Returns:
            None
        """
        for key, value in data.items():
            setattr(instance, key, value)
        self.session.add(instance)
        await self.session.flush()

    async def delete_one(self, record_id: int) -> None:
        """
        Deletes a record identified by its ID.

        Args:
            record_id (int): The ID of the record to delete.

        Returns:
            None
        """
        stmt = delete(self.model).where(self.model.id == record_id)
        await self.session.execute(stmt)

    async def find_one_or_none(self, **filter_by):
        """
        Finds a single record that matches the filter, or returns None if not found.

        Args:
            filter_by: Keyword arguments for filtering.

        Returns:
            The model instance or None.
        """
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def find_all(self):
        """
        Finds all records for the model.

        Returns:
            A list of all model instances.
        """
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_one(self, **filter_by):
        """
        Finds a single record that matches the filter.

        Args:
            filter_by: Keyword arguments for filtering.

        Returns:
            The model instance.
        """
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def get_stale_records(self, threshold: datetime) -> List[ModelType]:
        """
        Retrieves records with outdated data based on the given threshold.

        Args:
            threshold (datetime): The date and time threshold for determining outdated data.

        Returns:
            List[ModelType]: List of records with outdated data.
        """
        stmt = select(self.model).where(self.model.last_updated < threshold)
        logger.info(f"Checking for companies with last_updated < {threshold}")
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def subscription_exists(self, user_id: int, company_id: int) -> bool:
        """
        Checks if the user's subscription to the company exists.

        Args:
            user_id(int): User ID.
            company_id(int): Company ID.

        Returns:
            bool: True if the subscription exists, otherwise False.
        """
        result = await self.session.execute(
            select(self.model).filter_by(user_id=user_id, company_id=company_id)
        )
        return result.scalar_one_or_none() is not None

    async def add_subscription(self, user_id: int, company_id: int):
        """
        Adds a user subscription to company updates.

        Args:
            user_id(int): User ID.
            company_id(int): Company ID.
        """
        stmt = insert(self.model).values(user_id=user_id, company_id=company_id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_users_subscribed_to_company(self, company_id: int) -> List[User]:
        """
        Gets a list of users subscribed to company updates.

        Args:
            company_id (int): Company ID.

        Returns:
            List[User]: List of users subscribed to the company.
        """
        result = await self.session.execute(
            select(User).join(self.model).filter(self.model.company_id == company_id)
        )
        return result.scalars().all()
