from typing import Any

from starlette import status


class ObjectNotFound(Exception):
    def __init__(self, model_name: str, id_: Any) -> None:
        self.msg = f"{model_name} with given identifier - {id_} not found."
        self.status_code = status.HTTP_404_NOT_FOUND
        super().__init__(self.msg)


class ObjectAlreadyExists(Exception):
    def __init__(self, model_name: str, attr: str) -> None:
        self.msg = f"{model_name} with given attribute: {attr} already exists."
        self.status_code = status.HTTP_409_CONFLICT
        super().__init__(self.msg)


class EmailSendError(Exception):
    def __init__(self, email: str, action: str = "send templates"):
        self.msg = f"Failed to {action} to {email}. Please try again."
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        super().__init__(self.msg)


class PermissionDeniedError(Exception):
    def __init__(self, action: str = "perform this action"):
        self.msg = f"You don't have the necessary permissions to {action}."
        self.status_code = status.HTTP_403_FORBIDDEN
        super().__init__(self.msg)


class UserAlreadyExistsError(ObjectAlreadyExists):
    def __init__(self, email: str):
        super().__init__(model_name="User", attr=email)
        self.email = email


class UserNotFoundError(ObjectNotFound):
    def __init__(self, user_id: Any):
        super().__init__("User", user_id)


class AuthenticationError(Exception):
    pass


class InvalidCredentialsError(AuthenticationError):
    def __init__(self):
        self.msg = "Invalid credentials provided for user."
        self.status_code = status.HTTP_401_UNAUTHORIZED
        super().__init__(self.msg)


class EmailNotConfirmedError(AuthenticationError):
    def __init__(self):
        self.msg = "Email address has not been confirmed."
        self.status_code = status.HTTP_400_BAD_REQUEST
        super().__init__(self.msg)


class InvalidTokenError(AuthenticationError):
    def __init__(self):
        self.msg = "The provided token is invalid or expired."
        self.status_code = status.HTTP_400_BAD_REQUEST
        super().__init__(self.msg)


class PasswordResetError(AuthenticationError):
    def __init__(self):
        self.msg = "Failed to reset password. Please try again."
        self.status_code = status.HTTP_400_BAD_REQUEST
        super().__init__(self.msg)


class UserNotAuthenticatedError(AuthenticationError):
    def __init__(self):
        self.msg = "User is not authenticated. Please provide valid credentials."
        self.status_code = status.HTTP_401_UNAUTHORIZED
        super().__init__(self.msg)


class SuperuserPermissionError(PermissionDeniedError):
    def __init__(self, action: str = "manage permissions"):
        self.msg = f"Only superusers can {action}."
        self.status_code = status.HTTP_403_FORBIDDEN
        super().__init__(self.msg)
