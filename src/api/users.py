from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import UOWDep
from src.schemas import users
from src.utils.unit_of_work import UnitOfWork

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/{user_id}", response_model=users.UserInDB)
async def read_user(user_id: int, uow: UnitOfWork = Depends(UOWDep)):
    db_user = await uow.users.find_one(id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
