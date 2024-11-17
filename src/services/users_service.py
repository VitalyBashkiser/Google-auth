from src.exceptions.errors import UserNotFoundError, UserNotAuthenticatedError
from src.services.auth_service import AuthService
from src.utils.unitofwork import UnitOfWork


class UsersService:
    async def get_user_by_id(self,
                             uow: UnitOfWork,
                             auth_service: AuthService,
                             user_id: int,
                             jwt_token: str | None
                             ):
        """
        Retrieves a user by their ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            auth_service (AuthService): The auth service for database transactions.
            user_id (int): The ID of the user to be retrieved.
            jwt_token (User): The currently authenticated user.

        Returns:
            UserResponse: The user data.

        Raises:
            Exception: If the user with the specified ID is not found.
        """
        if not await auth_service.get_current_user(jwt_token, uow):
            raise UserNotAuthenticatedError

        async with uow:
            if user := await uow.users.find_one_or_none(id=user_id):
                return user
            raise UserNotFoundError


user_service = UsersService()
