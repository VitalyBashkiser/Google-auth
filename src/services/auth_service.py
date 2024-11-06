from src.services.email_service import email_service
from src.utils import auth_jwt
from src.utils.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    EmailNotConfirmedError,
    InvalidTokenError,
)
from src.models.users import User
from src.schemas import users
from src.utils.unit_of_work import UnitOfWork


async def register_user(user: users.UserCreate, uow: UnitOfWork) -> User:
    existing_user = await uow.users.get_by_email(user.email)
    if existing_user:
        raise UserAlreadyExistsError("A user with this email already exists.")

    hashed_password = auth_jwt.hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    await uow.users.add(new_user)
    await uow.commit()

    confirm_token = auth_jwt.create_confirmation_token(new_user.email)
    host = "http://localhost:8000"
    await email_service.reset_password(confirm_token, new_user.email, host)

    return new_user


async def login_user(user: users.UserCreate, uow: UnitOfWork):
    db_user = await uow.users.get_by_email(user.email)
    if not db_user or not auth_jwt.verify_password(user.password, db_user.hashed_password):
        raise InvalidCredentialsError("Invalid credentials.")

    if not db_user.is_email_confirmed:
        raise EmailNotConfirmedError("Email not confirmed.")

    return {"access_token": auth_jwt.create_access_token({"sub": db_user.email}), "token_type": "bearer"}


async def reset_password(email: str, uow: UnitOfWork):
    db_user = await uow.users.get_by_email(email)
    if not db_user:
        raise UserNotFoundError("There is no such user.")

    reset_token = auth_jwt.create_reset_token(email)
    host = "http://localhost:8000"
    await email_service.reset_password(reset_token, email, host)


async def confirm_registration(token: str, uow: UnitOfWork):
    email = auth_jwt.verify_confirmation_token(token)
    if email is None:
        raise InvalidTokenError("Invalid or expired token.")

    db_user = await uow.users.get_by_email(email)
    if not db_user:
        raise UserNotFoundError("User not found.")

    db_user.is_email_confirmed = True
    await uow.commit()
