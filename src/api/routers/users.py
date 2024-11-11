from fastapi import APIRouter, Depends

from src.models.users import User
from src.schemas.users import UserInDB
from src.services.users_service import user_service
from src.api.dependencies import UOWDep
from src.utils.auth_jwt import CheckHTTPBearer

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/{user_id}", response_model=UserInDB)
async def read_user(uow: UOWDep, user_id: int, jwt_token: str | None = Depends(CheckHTTPBearer())):
    """Retrieve a user by their ID.

    Args:
        user_id (int): ID of the user.
        uow (UOWDep): Dependency for the unit of work.
        jwt_token (User): The current user, must be an admin.

    Returns:
        UserResponse: Response containing user data.
    """
    return await user_service.get_user_by_id(uow, user_id, jwt_token)
