class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class EmailNotConfirmedError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class PasswordResetError(Exception):
    pass
