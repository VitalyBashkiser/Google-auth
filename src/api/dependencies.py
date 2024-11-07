from typing import Annotated

from fastapi import Depends

from src.utils.unitofwork import UnitOfWork, ABCUnitOfWork

UOWDep = Annotated[ABCUnitOfWork, Depends(UnitOfWork)]
