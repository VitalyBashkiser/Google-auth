from datetime import datetime

from src.enums.messages import Messages
from src.enums.permissions import Permission
from src.exceptions.errors import (
    UserNotFoundError,
)
from src.models.users import User
from src.utils.template_renderer import render_message

from src.utils.unitofwork import UnitOfWork


class AdminService:
    @staticmethod
    async def grant_permission(uow: UnitOfWork,
                               user_id: int,
                               permission: Permission,
                               ):
        """
        Grant a specific permission to a user if the current user is a superuser.

        Args:
            uow (ABCUnitOfWork): The unit of work instance for database transactions.
            user_id (int): ID of the user to grant permission to.
            permission (Permission): The permission to be granted.

        Raises:
            SuperuserPermissionError: If the current user is not a superuser.
        """
        async with uow:
            user = await uow.users.find_one_or_none(id=user_id)
            if not user:
                raise UserNotFoundError

            user_email = user.email

            if user.permissions is None:
                user.permissions = []

            if permission not in user.permissions:
                user.permissions.append(permission)
                await uow.users.update_one(user.id, {"permissions": user.permissions})
            await uow.commit()

            context = {
                "username": user_email,
                "permission": permission.value,
                "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return await render_message(Messages.PERMISSION_GRANTED, context)

    @staticmethod
    async def revoke_permission(uow: UnitOfWork,
                                user_id: int,
                                permission: Permission,
                                ):
        """
        Revoke a specific permission from a user if the current user is a superuser.

        Args:
            uow (ABCUnitOfWork): The unit of work instance for database transactions.
            user_id (int): ID of the user to revoke permission from.
            permission (Permission): The permission to be revoked.

        Raises:
            SuperuserPermissionError: If the current user is not a superuser.
        """
        async with uow:
            user = await uow.users.find_one_or_none(id=user_id)
            if not user:
                raise UserNotFoundError

            user_email = user.email
            if user.permissions is None:
                user.permissions = []

            if permission in user.permissions:
                user.permissions.remove(permission)
                await uow.users.update_one(user.id, {"permissions": user.permissions})
            await uow.commit()

            context = {
                "username": user_email,
                "permission": permission.value,
                "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return await render_message(Messages.PERMISSION_REVOKED, context)


    @staticmethod
    async def access_admin_panel():
        """
        Render the admin panel access message as HTML.
        """
        context = {"title": "Admin Panel Access", "content": "Welcome to the admin panel!"}
        return await render_message(Messages.ACCESS_ADMIN_PANEL, context)

    @staticmethod
    async def access_files():
        """
        Render the access files message as HTML.
        """
        context = {"title": "File Access", "content": "You have access to files."}
        return await render_message(Messages.ACCESS_FILES, context)

    def has_permission(self, user: User, permission: Permission) -> bool:
        return permission in user.permissions


admin_service = AdminService()
