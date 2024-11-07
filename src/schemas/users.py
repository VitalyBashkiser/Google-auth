from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    password: str


class SchemeLoginUser(UserBase):
    pass


class SchemeRegisterUser(UserBase):
    pass


class SchemeResetPassword(UserBase):
    pass


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_email_confirmed: bool

    class Config:
        from_attributes = True


class SchemeConfirmRegistration(BaseModel):
    confirm_reg_token: str
