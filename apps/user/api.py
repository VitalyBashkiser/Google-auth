from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from apps.schemas import user
from apps.user.models import User

router = APIRouter()


@router.get("/{user_id}", response_model=user.UserInDB)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User=user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
