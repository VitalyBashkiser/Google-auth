from typing import Annotated

from fastapi import Depends

from src.services.auth_service import AuthService
from src.utils.unitofwork import UnitOfWork, ABCUnitOfWork

UOWDep = Annotated[ABCUnitOfWork, Depends(UnitOfWork)]


def get_auth_service() -> AuthService:
    return AuthService()
