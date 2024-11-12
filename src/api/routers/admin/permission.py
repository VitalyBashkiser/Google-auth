from fastapi import APIRouter
from starlette import status

from src.api.dependencies import UOWDep, AdminServiceDep
from src.enums.permissions import Permission

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.post("/grant_permission/{user_id}", status_code=status.HTTP_200_OK)
async def grant_permission(
    uow: UOWDep,
    user_id: int,
    permission: Permission,
    admin_service: AdminServiceDep,
    # superuser: SuperuserDep
):
    """
    Grant a specific permission to a user.

    This endpoint allows a superuser to grant a specific permission to another user.
    The current user must have superuser status to perform this action.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        user_id (int): The ID of the user to whom the permission will be granted.
        permission (Permission): The permission to be granted.
        admin_service (AdminServiceDep): Dependency for admin services.

    Returns:
        dict: A message indicating that the permission has been granted.
    """
    return await admin_service.grant_permission(uow, user_id, permission)


@router.post("/revoke_permission/{user_id}", status_code=status.HTTP_200_OK)
async def revoke_permission(
    uow: UOWDep,
    user_id: int,
    permission: Permission,
    admin_service: AdminServiceDep,
):
    """
    Revoke a specific permission from a user.

    This endpoint allows a superuser to revoke a specific permission from another user.
    The current user must have superuser status to perform this action.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        user_id (int): The ID of the user from whom the permission will be revoked.
        permission (Permission): The permission to be revoked.
        admin_service (AdminServiceDep): Dependency for admin services.

    Returns:
        dict: A message indicating that the permission has been revoked.
    """
    return await admin_service.revoke_permission(uow, user_id, permission)
