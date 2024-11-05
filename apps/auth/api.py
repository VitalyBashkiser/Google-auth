from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db
from apps import utils
from apps.auth.email_service import email_service
from apps.schemas import user
from apps.user.models import User

router = APIRouter()


@router.post("/register", response_model=user.UserInDB)
async def register(user: user.UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    confirm_token = utils.create_confirmation_token(user.email)
    host = "http://localhost:8000"
    await email_service.reset_password(confirm_token, user.email, host)

    return db_user


@router.post("/login")
def login(user: user.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(email=user.email).first()
    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return {"access_token": "fake-jwt-token", "token_type": "bearer"}


@router.post("/password_reset")
async def password_reset(user: user.ResetPassword, db: Session = Depends(get_db)):
    email = user.email

    db_user = db.query(User).filter(email=email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is no such user.")

    reset_token = utils.create_reset_token(email)

    host = "http://localhost:8000"
    await email_service.reset_password(reset_token=reset_token, email=email, host=host)

    return {"detail": "Password reset email sent"}


@router.post("/confirmation_of_registration")
async def confirm_registration(user: user.ConfirmRegistration, db: Session = Depends(get_db)):
    email = utils.verify_confirmation_token(user.confirm_registration_token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired email confirmation link.",
        )

    db_user = db.query(User).filter(User=email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    db_user.is_email_confirmed = True
    db.add(db_user)
    db.commit()

    return {"result": "Email confirmed successfully."}
