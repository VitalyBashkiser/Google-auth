from loguru import logger

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import UOWDep
from src.services.auth_service import register_user, login_user, reset_password
from src.schemas import users, auth
from src.utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from src.utils.unit_of_work import UnitOfWork

router = APIRouter(
    prefix="/services",
    tags=["Auth"],
)


@router.post("/register", response_model=users.UserInDB)
async def register(scheme_register_user: users.UserCreate, uow: UnitOfWork = Depends(UOWDep)):
    """
    Register a new user.
    """
    logger.info(f"Received: {scheme_register_user}")
    try:
        return await register_user(scheme_register_user, uow)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login")
async def login(scheme_login_user: users.UserCreate, uow: UnitOfWork = Depends(UOWDep)):
    """
    Login user and return access token.
    """
    try:
        return await login_user(scheme_login_user, uow)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/password_reset")
async def password_reset(scheme_reset_password: auth.ResetPassword, uow: UnitOfWork = Depends(UOWDep)):
    """
    Reset password for the user.
    """
    await reset_password(scheme_reset_password.email, uow)
    return {"detail": "Password reset email sent"}


@router.post("/confirmation_of_registration")
async def confirm_registration(scheme_confirm_reset_password: auth.ConfirmRegistration, uow: UnitOfWork = Depends(UOWDep)):
    """
    Confirm registration using the confirmation token.
    """
    await confirm_registration(scheme_confirm_reset_password, uow)
    return {"result": "Email confirmed successfully."}
