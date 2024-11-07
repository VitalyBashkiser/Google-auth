from src.exceptions.errors import UserNotFoundError
from src.utils.unitofwork import UnitOfWork


class UsersService:
    async def get_user_by_id(self, uow: UnitOfWork, user_id: int):
        """
        Retrieves a user by their ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            user_id (int): The ID of the user to be retrieved.

        Returns:
            UserResponse: The user data.

        Raises:
            Exception: If the user with the specified ID is not found.
        """
        user = await uow.users.find_one(id=user_id)
        if user is None:
            raise UserNotFoundError(model_name="User")
        return user


user_service = UsersService()
