import traceback

from fastapi import APIRouter
from starlette import status

from src.api.dependencies import permission_dep, AdminServiceDep
from src.enums.permissions import Permission

router = APIRouter(
    prefix="/protected",
    tags=["Protected"]
)


@router.get("/files", status_code=status.HTTP_200_OK)
async def access_files(
        admin_service: AdminServiceDep,
        permission: None = permission_dep(Permission.ACCESS_ADMIN_PANEL)
):
    """
    Access files.

    This endpoint allows users with the 'access_files' permission to access files.
    """
    return await admin_service.access_files()


@router.get("/admin_panel", status_code=status.HTTP_200_OK)
async def access_admin_panel(
        admin_service: AdminServiceDep,
        permission: None = permission_dep(Permission.ACCESS_ADMIN_PANEL)
):
    """
    Access admin panel.

    This endpoint allows users with the 'access_admin_panel' permission to access the admin panel.
    """
    return await admin_service.access_admin_panel()
