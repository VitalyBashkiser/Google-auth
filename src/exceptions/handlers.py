from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from src.exceptions.errors import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    EmailNotConfirmedError,
    InvalidTokenError,
    PasswordResetError,
)

app = FastAPI()


async def user_not_found_handler(_: Request, exc: UserNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": str(exc.msg)})


async def user_already_exists_handler(_: Request, exc: UserAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": str(exc.msg)})


async def invalid_credentials_handler(_: Request, exc: InvalidCredentialsError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": str(exc.msg)})


async def email_not_confirmed_handler(_: Request, exc: EmailNotConfirmedError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(exc.msg)})


async def invalid_token_handler(_: Request, exc: InvalidTokenError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(exc.msg)})


async def handle_password_reset_error(_: Request, exc: PasswordResetError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": exc.msg})
