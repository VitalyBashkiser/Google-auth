from src.exceptions.errors import UserNotFoundError, UserNotAuthenticatedError
from src.utils.unitofwork import UnitOfWork


class UsersService:
    async def get_user_by_id(self, uow: UnitOfWork, user_id: int, jwt_token: str | None):
        """
        Retrieves a user by their ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            user_id (int): The ID of the user to be retrieved.
            jwt_token (User): The currently authenticated user.

        Returns:
            UserResponse: The user data.

        Raises:
            Exception: If the user with the specified ID is not found.
        """
        current_user = await self.get_current_user(jwt_token, uow)
        if not current_user:
            raise UserNotAuthenticatedError

        async with uow:
            user = await uow.users.find_one(id=user_id)
            if not user:
                raise UserNotFoundError
            return user


user_service = UsersService()
