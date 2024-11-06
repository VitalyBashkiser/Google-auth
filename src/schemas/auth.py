from pydantic import BaseModel, EmailStr


class ConfirmRegistration(BaseModel):
    confirm_registration_token: str


class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str
