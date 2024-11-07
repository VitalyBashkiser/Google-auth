from fastapi import APIRouter

from src.api.dependencies import UOWDep
from src.schemas.users import (
    SchemeConfirmRegistration,
    SchemeResetPassword,
    SchemeRegisterUser,
    SchemeLoginUser,
    UserInDB,
)
from src.services.auth_service import auth_service
from src.exceptions.errors import (
    InvalidTokenError,
    UserNotFoundError,
)
from src.services.users_service import user_service

router = APIRouter(
    prefix="/services",
    tags=["Auth"],
)


@router.post("/register", response_model=UserInDB)
async def register(uow: UOWDep, user: SchemeRegisterUser):
    """Register a new user.

    This endpoint allows a new user to register by providing user details. After successful registration, the details of the created user are returned.

    Args:
        user (SchemeRegisterUser): The user details required for registration, including email, password, and any other necessary information.
        uow (UOWDep): Dependency for unit of work management.
        auth_service (UsersService): Service for managing user-related operations.

    Returns:
        UserSchema: Details of the newly created user.

    Raises:
        Exception: May raise an Exception if registration fails.
    """
    async with uow:
        user_id = await auth_service.register_user(uow, user)
        print("---")
        created_user = await user_service.get_user_by_id(uow, user_id)
        return created_user


@router.post("/login")
async def login(uow: UOWDep, user: SchemeLoginUser):
    """Authenticate a user and generate a token.

    This endpoint allows a user to login by providing email and password. Upon successful authentication, an access token is generated and returned.

    Args:
        user (SchemeLoginUser): The user's credentials including email and password.
        uow (UOWDep): Dependency for unit of work management.
        auth_service (AuthService): Service for managing authentication operations.

    Returns:
        TokenResponse: Contains the access token and the token type.

    Raises:
        Exception: May raise an Exception if authentication fails.
    """
    db_user = await auth_service.authenticate_user(uow, user.email, user.password)
    access_token = await auth_service.create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/password_reset")
async def password_reset(scheme_reset_password: SchemeResetPassword, uow: UOWDep):
    """
    Reset the password for a user.

    This endpoint allows a user to initiate the password reset process by providing their email address.
    If the email is associated with an existing user, a password reset email containing a reset token will be sent.
    The user can then use this token to set a new password.

    Args:
        scheme_reset_password (SchemeResetPassword): The schema containing the user's email address for the password reset.
        uow (UOWDep): Dependency for unit of work management, which handles database transactions.

    Returns:
        dict: A response indicating that the password reset email has been sent.

    Raises:
        UserNotFoundError: If no user is found with the provided email address, an exception is raised,
                           indicating that the user does not exist.
    """
    try:
        await auth_service.password_reset(uow=uow, scheme_reset_password=scheme_reset_password)
        return {"detail": "Password reset email sent"}
    except UserNotFoundError as e:
        raise e


@router.post("/confirmation_of_registration")
async def confirm_registration(scheme_confirm_registration: SchemeConfirmRegistration, uow: UOWDep):
    """
    Confirm the registration of a user using a confirmation token.

    This endpoint allows a user to confirm their registration by providing a confirmation token received via email.
    If the token is valid and corresponds to an existing user, the user's email status will be updated to confirmed.

    Args:
        scheme_confirm_registration (SchemeConfirmRegistration): The schema containing the confirmation token
                                                                and any necessary user details for the confirmation.
        uow (UOWDep): Dependency for unit of work management, facilitating database operations during the confirmation.

    Returns:
        dict: A response indicating that the email has been confirmed successfully.

    Raises:
        InvalidTokenError: If the provided confirmation token is invalid or expired, an exception is raised,
                           indicating the issue with the token.
        UserNotFoundError: If no user is found associated with the provided confirmation token, an exception is raised,
                           indicating that the user does not exist.
    """
    try:
        await confirm_registration(scheme_confirm_registration, uow)
        return {"result": "Email confirmed successfully."}
    except InvalidTokenError as e:
        raise e
    except UserNotFoundError as e:
        raise e
