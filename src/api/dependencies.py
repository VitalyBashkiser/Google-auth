from typing import Annotated

from fastapi import Depends

from src.enums.permissions import Permission
from src.exceptions.errors import PermissionDeniedError
from src.models.users import User
from src.services.admin_service import AdminService
from src.services.auth_service import AuthService
from src.utils.auth_jwt import CheckHTTPBearer
from src.utils.unitofwork import UnitOfWork, ABCUnitOfWork

UOWDep = Annotated[ABCUnitOfWork, Depends(UnitOfWork)]
AuthServiceDep = Annotated[AuthService, Depends(AuthService)]
JWTTokenDep = Annotated[str | None, Depends(CheckHTTPBearer())]
UserDep = Annotated[User, Depends(AuthService().get_current_user)]
AdminServiceDep = Annotated[AdminService, Depends(AdminService)]


async def is_superuser(current_user: UserDep) -> UserDep:
    """
    Dependency to ensure the current user is a superuser.
    """
    if not current_user.is_superuser:
        raise PermissionDeniedError("Only superusers can revoke permissions.")
    return current_user

SuperuserDep = Annotated[User, Depends(is_superuser)]


def permission_dep(permission: Permission) -> Annotated[None, Depends]:
    def checker(user: UserDep):
        require_permission(permission, user)
    """
    Dependency to check if the current user has the specified permission.

    Args:
        permission (Permission): The permission to check for.

    Returns:
        Annotated[None, Depends]: Dependency to be used in route handlers.
    """
    return Depends(checker)


def require_permission(permission: Permission):
    if not is_superuser and permission not in permission_dep:
        raise PermissionDeniedError(f"access {permission}")
