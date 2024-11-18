from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from src.exceptions.errors import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    EmailNotConfirmedError,
    InvalidTokenError,
    PasswordResetError,
    EmailSendError,
    UserNotAuthenticatedError,
    PermissionDeniedError,
    SuperuserPermissionError,
    ObjectNotFound,
    AlreadySubscribedError,
)

app = FastAPI()


async def object_not_found_handler(_: Request, exc: ObjectNotFound) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": str(exc.msg)})


async def user_already_exists_handler(_: Request, exc: UserAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": str(exc.msg)})


async def invalid_credentials_handler(_: Request, exc: InvalidCredentialsError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": str(exc.msg)})


async def email_not_confirmed_handler(_: Request, exc: EmailNotConfirmedError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(exc.msg)})


async def invalid_token_handler(_: Request, exc: InvalidTokenError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(exc.msg)})


async def handle_password_reset_error(_: Request, exc: PasswordResetError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": exc.msg})


async def email_send_error_handler(_: Request, exc: EmailSendError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(exc.msg)})


async def user_not_authenticated_handler(_: Request, exc: UserNotAuthenticatedError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": exc.msg})


async def permission_denied_error_handler(_: Request, exc: PermissionDeniedError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.msg)}
    )


async def superuser_permission_error_handler(_: Request, exc: SuperuserPermissionError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.msg)}
    )


async def already_subscribe_error_handler(_: Request, exc: AlreadySubscribedError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"message": str(exc.msg)})
