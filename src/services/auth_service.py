from src.core.config.database import settings
from src.models.users import User
from src.services.email_service import email_service
from src.utils import auth_jwt
from src.exceptions.errors import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    EmailNotConfirmedError,
    InvalidTokenError,
)
from src.schemas.users import SchemeRegisterUser
from src.utils.unitofwork import UnitOfWork


class AuthService:
    async def register_user(self, uow: UnitOfWork, user: SchemeRegisterUser) -> int:
        """
        Adds a new user to the database.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            user (SchemeRegisterUser): The schema containing user data to be added.

        Returns:
            int: The ID of the newly added user.

        Raises:
            Exception: If a user with the provided email already exists.
        """
        existing_user = await uow.users.find_one_or_none(email=user.email)
        if existing_user:
            raise UserAlreadyExistsError("A user with this email already exists.")

        hashed_password = auth_jwt.hash_password(user.password)
        new_user = User(email=user.email, hashed_password=hashed_password)
        await uow.users.add_user(new_user)

        confirm_token = auth_jwt.create_confirmation_token(new_user.email)
        host = settings.POSTGRES_HOST
        await email_service.send_confirmation_email(confirm_token, new_user.email, host)
        return new_user.id

    async def login_user(self, uow: UnitOfWork, email: str, password: str):
        """
        Authenticate a user by their email and password.

        Args:
            uow (IUnitOfWork): The unit of work instance for database transactions.
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            User: The authenticated user.

        Raises:
            Exception: If the credentials are invalid.
        """
        db_user = await uow.users.find_one_or_none(email=email)
        if not db_user:
            raise InvalidCredentialsError("Invalid credentials.")

        if not auth_jwt.verify_password(password, db_user.hashed_password):
            raise InvalidCredentialsError("Invalid credentials.")

        if not db_user.is_email_confirmed:
            raise EmailNotConfirmedError("Email not confirmed.")

        return {"access_token": auth_jwt.create_access_token({"sub": db_user.email}), "token_type": "bearer"}

    async def reset_password(self, uow: UnitOfWork, email: str):
        """
        Initiate the password reset process for a user.

        This method generates a reset token and sends it to the user's email address.
        The user can then use this token to reset their password.

        Args:
            uow (UnitOfWork): The unit of work used for database transactions.
            email (str): The email address of the user requesting a password reset.

        Returns:
            None: This method does not return a value.

        Raises:
            UserNotFoundError: If no user with the given email exists.
        """
        db_user = await uow.users.find_one_or_none(email=email)
        if not db_user:
            raise UserNotFoundError("There is no such user.")

        reset_token = auth_jwt.create_reset_token(email)
        host = "http://localhost:8000"
        await email_service.reset_password(reset_token, email, host)

    async def confirm_registration(self, uow: UnitOfWork, token: str):
        """
        Confirm the registration of a user.

        This method verifies the confirmation token sent to the user's email.
        If the token is valid and corresponds to an existing user, the user's email status is updated to confirmed.

        Args:
            uow (UnitOfWork): The unit of work used for database transactions.
            token (str): The confirmation token sent to the user's email.

        Returns:
            None: This method does not return a value.

        Raises:
            InvalidTokenError: If the confirmation token is invalid or expired.
            UserNotFoundError: If no user is found associated with the provided email.
        """
        email = auth_jwt.verify_confirmation_token(token)
        if email is None:
            raise InvalidTokenError("Invalid or expired token.")

        db_user = await uow.users.find_one_or_none(email=email)
        if not db_user:
            raise UserNotFoundError("User not found.")

        db_user.is_email_confirmed = True


auth_service = AuthService()
