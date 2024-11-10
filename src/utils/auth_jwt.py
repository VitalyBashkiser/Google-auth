from datetime import datetime, timedelta
from typing import Optional

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
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_change_email_token(old_email: str, new_email: str) -> str:
    data = {"old_email": old_email, "new_email": new_email}
    return create_access_token(data, expires_delta=timedelta(hours=1))


def create_confirmation_token(email: str) -> str:
    return create_access_token({"sub": email}, expires_delta=timedelta(hours=1))


def create_reset_token(email: str) -> str:
    return create_access_token({"sub": email}, expires_delta=timedelta(minutes=15))


def verify_confirmation_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def verify_change_email_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"old_email": payload.get("old_email"), "new_email": payload.get("new_email")}
    except JWTError:
        return None


class CheckHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials or credentials.scheme != "Bearer":
            raise UserNotAuthenticatedError
        return credentials.credentials
