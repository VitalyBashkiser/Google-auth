from pydantic import BaseModel, EmailStr


class OneTokenSchema(BaseModel):
    token: str


class ResetPasswordSchema(BaseModel):
    """
    Schema for password reset request, contains user email.
    """

    email: EmailStr


class ResetPasswordConfirmSchema(BaseModel):
    """
    Schema for password reset confirmation, contains new password and token.
    """

    new_password: str
    token: str


class EmailChangeSchema(BaseModel):
    """
    Schema for email change, contains old and new email.
    """

    old_email: EmailStr
    new_email: EmailStr
