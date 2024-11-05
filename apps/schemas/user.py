from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class ConfirmRegistration(BaseModel):
    confirm_registration_token: str


class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_email_confirmed: bool

    class Config:
        orm_mode = True
