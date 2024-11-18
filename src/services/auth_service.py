from fastapi import Depends
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config.app_settings import AppSettings
from src.core.config.database import settings
from src.enums.messages import Messages
from src.models.users import User
from src.services.email_service import email_service
from src.utils import auth_jwt
from src.exceptions.errors import (
    UserNotFoundError,
    InvalidCredentialsError,
    EmailNotConfirmedError,
    UserAlreadyExistsError,
    InvalidTokenError,
    EmailSendError,
    UserNotAuthenticatedError,
)
from src.schemas.users import SchemeRegisterUser
from src.schemas.auth import EmailChangeSchema
from src.utils.auth_jwt import CheckHTTPBearer
from src.utils.unitofwork import UnitOfWork, ABCUnitOfWork


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = "HS256"

    async def register_user(self, uow: UnitOfWork, user: SchemeRegisterUser):
        """
        Adds a new user to the database.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            user (SchemeRegisterUser): The schema containing user data to be added.

        Returns:
            int: The ID of the newly added user.

        Raises:
            Exception: If a user with the provided templates already exists.
        """
        user_dict = user.model_dump()
        async with uow:
            if await uow.users.find_one_or_none(email=user_dict["email"]):
                raise UserAlreadyExistsError(user_dict["email"])

            user_id = await uow.users.add_one(user_dict)

            confirm_token = auth_jwt.create_confirmation_token(user_dict["email"])
            host = AppSettings.HOST
            if not await email_service.confirm_email(
                    username=user_dict["email"],
                    token=confirm_token,
                    email=user_dict["email"],
                    host=host,
                    email_type=Messages.EMAIL_CONFIRMATION
            ):
                raise EmailSendError(email=user_dict["email"], action="send confirmation email")
            return user_id

    async def confirm_verification_email(self, uow: ABCUnitOfWork, token: str):
        """
        Confirm the registration of a user by updating the templates confirmation status.

        Args:
            uow (ABCUnitOfWork): The unit of work instance for database transactions.
            token: (str): The token of the user whose registration is being confirmed.
        Returns:
            UserResponse: The updated user data.

        Raises:
            Exception: If the user with the specified templates is not found.
        """
        email = auth_jwt.verify_confirmation_token(token)
        if email is None:
            raise InvalidTokenError

        async with uow:
            user = await uow.users.find_one_or_none(email=email)

            if not user:
                raise InvalidCredentialsError

            is_email_confirmed = True
            data = {"is_email_confirmed": is_email_confirmed, "email": email}

            await uow.users.update_one(user.id, data)
            await uow.commit()

            return

    async def login_user(self, uow: ABCUnitOfWork, email: str, password: str):
        """
        Authenticate a user by their templates and password.

        Args:
            uow (ABCUnitOfWork): The unit of work instance for database transactions.
            email (str): The user's templates.
            password (str): The user's password.

        Returns:
            User: The authenticated user.

        Raises:
            Exception: If the credentials are invalid.
        """
        async with uow:
            user = await uow.users.find_one_or_none(email=email)
            if not user:
                raise InvalidCredentialsError

            if not auth_jwt.verify_password(password, user.hashed_password):
                raise InvalidCredentialsError

            if not user.is_email_confirmed:
                raise EmailNotConfirmedError

            data = {"is_active": True}
            await uow.users.update_one(user.id, data)

            token_data = {"sub": user.email}
            access_token = auth_jwt.create_access_token(token_data)

            await uow.commit()
            return {"access_token": access_token, "token_type": "bearer"}

    async def reset_password(self, uow: UnitOfWork, email: str):
        """
        Initiate the password reset process for a user.

        This method generates a reset token and sends it to the user's templates address.
        The user can then use this token to reset their password.

        Args:
            uow (UnitOfWork): The unit of work used for database transactions.
            email (str): The templates address of the user requesting a password reset.

        Returns:
            None: This method does not return a value.

        Raises:
            UserNotFoundError: If no user with the given templates exists.
        """
        async with uow:
            user = await uow.users.find_one_or_none(email=email)
            if not user:
                raise UserNotFoundError

            reset_token = auth_jwt.create_reset_token(email)
            host = AppSettings.HOST
            await email_service.confirm_email(
                username=user.email,
                token=reset_token,
                email=email,
                host=host,
                email_type=Messages.PASSWORD_RESET
            )

    async def reset_confirm_password(self, uow: UnitOfWork, token: str, new_password: str):
        """
        Confirm the password reset and update it in the database.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            token (str): The reset token sent to the user's templates.
            new_password (str): The new password to be set for the user.

        Returns:
            None: This method does not return a value.

        Raises:
            InvalidTokenError: If the token is invalid or expired.
            UserNotFoundError: If the user associated with the token does not exist.
        """
        email = auth_jwt.verify_confirmation_token(token)
        if email is None:
            raise InvalidTokenError

        async with uow:
            user = await uow.users.find_one_or_none(email=email)
            if not user:
                raise UserNotFoundError

            hashed_password = auth_jwt.hash_password(new_password)
            data = {"hashed_password": hashed_password}
            await uow.users.update_one(user.id, data)
            await uow.commit()

    async def change_email(self, uow: UnitOfWork, data: EmailChangeSchema, jwt_token: str | None):
        """
        Initiate the process to change the user's templates address.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            data (str): The user's current templates and new templates.
            jwt_token (User): The currently authenticated user.

        Returns:
            None: This method does not return a value.

        Raises:
            UserNotFoundError: If the user with the current templates does not exist.
        """
        current_user = await self.get_current_user(jwt_token, uow)
        if not current_user:
            raise UserNotAuthenticatedError()

        async with uow:
            user = await uow.users.find_one_or_none(email=data.old_email)
            if not user:
                raise UserNotFoundError

            confirm_token = auth_jwt.create_change_email_token(data.old_email, data.new_email)
            host = AppSettings.HOST
            await email_service.confirm_email(
                username=user.email,
                token=confirm_token,
                email=data.new_email,
                host=host,
                email_type=Messages.CHANGE_EMAIL
            )
            await uow.commit()

    async def confirm_change_email(self, uow: UnitOfWork, token: str, jwt_token: str | None):
        """
        Confirm the templates change by validating the token and updating the user's templates.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            token (str): The token containing old and new templates addresses.
            jwt_token (User): The currently authenticated user.

        Returns:
            None: This method does not return a value.

        Raises:
            InvalidTokenError: If the token is invalid or expired.
            UserNotFoundError: If the user with the old templates does not exist.
        """
        current_user = await self.get_current_user(jwt_token, uow)
        if not current_user:
            raise UserNotAuthenticatedError()

        email_data = auth_jwt.verify_change_email_token(token)
        if not email_data:
            raise InvalidTokenError

        old_email = email_data["old_email"]
        new_email = email_data["new_email"]

        async with uow:
            user = await uow.users.find_one_or_none(email=old_email)
            if not user:
                raise UserNotFoundError

            data = {"email": new_email}
            await uow.users.update_one(user.id, data)

            await uow.commit()

    async def get_current_user(
        self,
        token: str = Depends(CheckHTTPBearer()),
        uow: UnitOfWork = Depends(UnitOfWork),
    ) -> User:
        """
        Retrieve the current user based on the provided JWT token.

        Args:
            token (str): The JWT token from the request.
            uow (UnitOfWork): The unit of work instance for database transactions.

        Returns:
            User: The currently authenticated user.

        Raises:
            UserNotAuthenticatedError: If the token is invalid or the user is not found.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise UserNotAuthenticatedError
            else:
                raise UserNotAuthenticatedError
        except JWTError:
            raise UserNotAuthenticatedError

        async with uow:
            user = await uow.users.find_one_or_none(email=email)
            if not user:
                raise UserNotAuthenticatedError
            return user

    async def get_current_user_id(
        self,
        token: str = Depends(CheckHTTPBearer()),
        uow: UnitOfWork = Depends(UnitOfWork)
    ) -> int:
        """
        Retrieve only the ID of the current user based on the provided JWT token.

        Args:
            token (str): The JWT token from the request.
            uow (UnitOfWork): The unit of work instance for database transactions.

        Returns:
            int: The ID of the currently authenticated user.

        Raises:
            UserNotAuthenticatedError: If the token is invalid or the user is not found.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload.get("sub")
            if not email:
                raise UserNotAuthenticatedError
        except JWTError:
            raise UserNotAuthenticatedError

        async with uow:
            user = await uow.users.find_one_or_none(email=email)
            if not user:
                raise UserNotAuthenticatedError
            return user.id

    async def decode_token(self, token: str) -> dict:
        """
        Decode a JWT token without verifying its validity.

        Args:
            token (str): The JWT token to decode.

        Returns:
            dict: The decoded token payload.

        Raises:
            HTTPException: If the token is invalid.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            raise UserNotAuthenticatedError


auth_service = AuthService()
