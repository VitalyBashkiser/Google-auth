from fastapi import APIRouter
from starlette import status

from src.api.dependencies import UOWDep, AuthServiceDep, JWTTokenDep
from src.models.users import User
from src.schemas.auth import (
    ResetPasswordConfirmSchema,
    ResetPasswordSchema,
    EmailChangeSchema,
    OneTokenSchema
)
from src.schemas.users import (
    SchemeConfirmRegistration,
    SchemeRegisterUser,
    SchemeLoginUser,
)
from src.services.auth_service import AuthService

router = APIRouter(
    prefix="/services",
    tags=["Auth"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(uow: UOWDep, user: SchemeRegisterUser, auth_service: AuthServiceDep):
    """Register a new user.

    This endpoint allows a new user to register by providing user details. After successful registration, the details of the created user are returned.

    Args:
        user (SchemeRegisterUser): The user details required for registration, including email, password, and any other necessary information.
        uow (UOWDep): Dependency for unit of work management.
        auth_service (UsersService): Service for managing user-related operations.

    Returns:
        UserSchema: Details of the newly created user.
    """
    await auth_service.register_user(uow, user)


@router.post("/verification_email")
async def verification_email(
        uow: UOWDep,
        token: SchemeConfirmRegistration,
        auth_service: AuthServiceDep
):
    """
    Confirm the registration of a user using a confirmation token.

    This endpoint allows a user to confirm their registration by providing a confirmation token received via email.
    If the token is valid and corresponds to an existing user, the user's email status will be updated to confirmed.

    Args:
        token (SchemeConfirmRegistration): The schema containing the confirmation token
                                                                and any necessary user details for the confirmation.
        uow (UOWDep): Dependency for unit of work management, facilitating database operations during the confirmation.
        auth_service (AuthService): Service for managing authentication operations.

    Returns:
        dict: A response indicating that the email has been confirmed successfully.
    """
    return await auth_service.confirm_verification_email(uow, token.token)


@router.post("/login")
async def login(uow: UOWDep, user: SchemeLoginUser, auth_service: AuthServiceDep):
    """Authenticate a user and generate a token.

    This endpoint allows a user to login by providing email and password. Upon successful authentication, an access token is generated and returned.

    Args:
        user (SchemeLoginUser): The user's credentials including email and password.
        uow (UOWDep): Dependency for unit of work management.
        auth_service (AuthService): Service for managing authentication operations.

    Returns:
        TokenResponse: Contains the access token and the token type.
    """
    return await auth_service.login_user(uow, user.email, user.password)


@router.post("/password_reset")
async def password_reset(
    uow: UOWDep,
    reset_password: ResetPasswordSchema,
    auth_service: AuthServiceDep,
    jwt_token: JWTTokenDep,
):
    """
    Reset the password for a user.

    This endpoint allows a user to initiate the password reset process by providing their email address.
    If the email is associated with an existing user, a password reset email containing a reset token will be sent.
    The user can then use this token to set a new password.

    Args:
        reset_password (SchemeResetPassword): The schema containing the user's email address for the password reset.
        uow (UOWDep): Dependency for unit of work management, which handles database transactions.
        auth_service (AuthService): Service for managing authentication operations.
        jwt_token (User): The currently authenticated user.

    Returns:
        dict: A response indicating that the password reset email has been sent.
    """
    return await auth_service.reset_password(uow, reset_password.email, jwt_token)


@router.post("/password_reset/confirm", status_code=status.HTTP_201_CREATED)
async def reset_password_confirm(
    uow: UOWDep,
    data: ResetPasswordConfirmSchema,
    auth_service: AuthServiceDep,
    jwt_token: JWTTokenDep,
):
    """
    Confirm the password reset with the provided token and new password.

    Args:
        data (ResetPassword): Contains the user's email, new password, and reset token.
        uow (UOWDep): Dependency for unit of work management.
        auth_service (AuthService): Service for managing authentication operations.
        jwt_token (User): The currently authenticated user.

    Returns:
        dict: A response indicating that the password has been successfully reset.
    """
    await auth_service.reset_confirm_password(uow, data.token, data.new_password, jwt_token)


@router.post("/change_email", status_code=status.HTTP_200_OK)
async def change_email(
    email_data: EmailChangeSchema,
    uow: UOWDep,
    auth_service: AuthServiceDep,
    jwt_token: JWTTokenDep,
):
    """
    Initiate the email change process for the user.

    Args:
        email_data (EmailSchema): Contains the user's current and new email.
        uow (UOWDep): Dependency for unit of work management.
        auth_service (AuthService): Service for managing authentication operations.
        jwt_token (User): The currently authenticated user.

    Returns:
        dict: A response indicating that the email change request has been sent.
    """
    return await auth_service.change_email(uow, email_data, jwt_token)


@router.post("/confirm_email_change", status_code=status.HTTP_200_OK)
async def confirm_email_change(
    data: OneTokenSchema,
    uow: UOWDep,
    auth_service: AuthServiceDep,
    jwt_token: JWTTokenDep,
):
    """
    Confirm the email change using the provided token.

    Args:
        data (OneTokenSchema): The token received in the email, containing old and new email addresses.
        uow (UOWDep): Dependency for unit of work management.
        auth_service (AuthService): Service for managing authentication operations.
        jwt_token (User): The currently authenticated user.

    Returns:
        dict: A response message indicating success or failure.
    """
    return await auth_service.confirm_change_email(uow, data.token, jwt_token)
