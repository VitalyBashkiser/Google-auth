from pydantic import BaseModel, EmailStr

from src.utils import auth_jwt


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr


class SchemeLoginUser(UserBase):
    pass


class SchemeRegisterUser(UserBase):
    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        data["hashed_password"] = auth_jwt.hash_password(data.pop("password"))
        return data


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_email_confirmed: bool

    class Config:
        from_attributes = True


class SchemeConfirmRegistration(BaseModel):
    token: str
