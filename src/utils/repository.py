from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar, List

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession


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
        res = await self.session.execute(stmt)
        return res.scalars().all()
