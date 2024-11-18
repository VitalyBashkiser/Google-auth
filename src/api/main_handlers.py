from fastapi import FastAPI
from src.exceptions.error_handler import ExceptionHandlerMiddleware
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
from src.exceptions.handlers import (
    user_already_exists_handler,
    invalid_credentials_handler,
    email_not_confirmed_handler,
    invalid_token_handler,
    handle_password_reset_error,
    email_send_error_handler,
    user_not_authenticated_handler,
    permission_denied_error_handler,
    superuser_permission_error_handler,
    object_not_found_handler,
    already_subscribe_error_handler,
)

exception_handlers = [
    (UserAlreadyExistsError, user_already_exists_handler),
    (InvalidCredentialsError, invalid_credentials_handler),
    (EmailNotConfirmedError, email_not_confirmed_handler),
    (InvalidTokenError, invalid_token_handler),
    (PasswordResetError, handle_password_reset_error),
    (EmailSendError, email_send_error_handler),
    (UserNotAuthenticatedError, user_not_authenticated_handler),
    (PermissionDeniedError, permission_denied_error_handler),
    (SuperuserPermissionError, superuser_permission_error_handler),
    (ObjectNotFound, object_not_found_handler),
    (AlreadySubscribedError, already_subscribe_error_handler),
]


def setup_handlers(app: FastAPI):
    """
    Function to add all exception handlers and middleware to the application.
    """
    for exception, handler in exception_handlers:
        app.add_exception_handler(exception, handler)

    app.add_middleware(ExceptionHandlerMiddleware)
