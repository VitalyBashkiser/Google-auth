from datetime import datetime, timedelta

from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import jwt, JWTError

from src.core.config.database import settings
from src.exceptions.errors import UserNotAuthenticatedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a plain-text password.

    This function hashes a plain-text password using bcrypt.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password.

    Compares a plain-text password with its hashed counterpart to confirm a match.

    Args:
        plain_password (str): The plain-text password.
        hashed_password (str): The hashed password to verify against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a new access token.

    Generates a JWT access token with the specified expiration time, storing
    any relevant user data.

    Args:
        data (dict): The data to encode within the token, typically user information.
        expires_delta (timedelta, optional): The token's lifetime. Defaults to 15 minutes.

    Returns:
        str: The generated JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "scope": "access_token"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_change_email_token(old_email: str, new_email: str) -> str:
    """Create a token for templates change confirmation.

    Generates a token to confirm a user's templates change request,
    encoding both old and new templates addresses.

    Args:
        old_email (str): The current templates of the user.
        new_email (str): The new templates address to be set for the user.

    Returns:
        str: The generated JWT token for templates change.
    """
    data = {"old_email": old_email, "new_email": new_email}
    return create_access_token(data, expires_delta=timedelta(hours=1))


def create_confirmation_token(email: str) -> str:
    """Create a confirmation token for user registration.

    Generates a token for confirming a new user's templates address upon registration.

    Args:
        email (str): The templates address to confirm.

    Returns:
        str: The generated JWT token for templates confirmation.
    """
    return create_access_token({"sub": email}, expires_delta=timedelta(hours=1))


def create_reset_token(email: str) -> str:
    """Create a password reset token.

    Generates a token for securely resetting a user's password,
    typically short-lived for security.

    Args:
        email (str): The templates address associated with the password reset.

    Returns:
        str: The generated JWT token for password reset.
    """
    return create_access_token({"sub": email}, expires_delta=timedelta(minutes=15))


def verify_confirmation_token(token: str) -> str | None:
    """Verify a confirmation token.

    Decodes and verifies a confirmation token to retrieve the associated templates.

    Args:
        token (str): The JWT token to verify.

    Returns:
        str | None: The templates address if verification is successful,
        or None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def verify_change_email_token(token: str) -> dict | None:
    """Verify an templates change token.

    Decodes and verifies an templates change token to retrieve the old
    and new templates addresses.

    Args:
        token (str): The JWT token to verify.

    Returns:
        dict | None: A dictionary with 'old_email' and 'new_email'
        if successful, or None if the token is invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"old_email": payload.get("old_email"), "new_email": payload.get("new_email")}
    except JWTError:
        return None


class CheckHTTPBearer(HTTPBearer):
    """HTTP Bearer authentication dependency for securing endpoints.

    This dependency verifies that requests contain a valid JWT in the
    Authorization header, using the Bearer scheme.

    Raises:
        UserNotAuthenticatedError: If no valid Bearer token is provided.

    Returns:
        str | None: The JWT token if authentication is successful,
        or None if authentication fails.
    """

    async def __call__(self, request: Request) -> str | None:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials or credentials.scheme != "Bearer":
            raise UserNotAuthenticatedError
        return credentials.credentials
