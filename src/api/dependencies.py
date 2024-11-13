from typing import Annotated

from fastapi import Depends

from src.services.auth_service import AuthService
from src.utils.auth_jwt import CheckHTTPBearer
from src.utils.unitofwork import UnitOfWork, ABCUnitOfWork

UOWDep = Annotated[ABCUnitOfWork, Depends(UnitOfWork)]
AuthServiceDep = Annotated[AuthService, Depends(AuthService)]
JWTTokenDep = Annotated[str | None, Depends(CheckHTTPBearer())]
