from fastapi import APIRouter

from src.exceptions.errors import UserNotFoundError
from src.schemas.users import UserInDB
from src.services.users_service import user_service
from src.api.dependencies import UOWDep

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/{user_id}", response_model=UserInDB)
async def read_user(uow: UOWDep, user_id: int):
    """Retrieve a user by their ID.

    Args:
        user_id (int): ID of the user.
        uow (UOWDep): Dependency for the unit of work.
        user_service (UsersService): Service for managing users.
        current_user (User): The current user, must be an admin.

    Returns:
        UserResponse: Response containing user data.
    """
    try:
        return await user_service.get_user_by_id(uow, user_id)
    except UserNotFoundError as e:
        raise e
