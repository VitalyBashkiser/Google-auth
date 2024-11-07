import uvicorn
from fastapi import FastAPI

from src.api.main_routers import main_router
from src.exceptions.error_handler import ExceptionHandlerMiddleware
from src.exceptions.errors import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    EmailNotConfirmedError,
    InvalidTokenError,
    PasswordResetError,
)
from src.exceptions.handlers import (
    user_not_found_handler,
    user_already_exists_handler,
    invalid_credentials_handler,
    email_not_confirmed_handler,
    invalid_token_handler,
    handle_password_reset_error,
)

app = FastAPI(title="Authorisation via Email")

app.add_exception_handler(UserNotFoundError, user_not_found_handler)
app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
app.add_exception_handler(EmailNotConfirmedError, email_not_confirmed_handler)
app.add_exception_handler(InvalidTokenError, invalid_token_handler)
app.add_exception_handler(PasswordResetError, handle_password_reset_error)
app.add_middleware(ExceptionHandlerMiddleware)


app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8090,
        reload=True,
    )
