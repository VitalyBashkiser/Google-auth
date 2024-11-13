from pydantic import BaseModel, EmailStr


class OneTokenSchema(BaseModel):
    """
    Schema representing a single token for various authentication purposes.

    Attributes:
        token (str): The token value used for actions like
        email verification or password reset.
    """

    token: str


class ResetPasswordSchema(BaseModel):
    """
    Schema for initiating a password reset request.

    Attributes:
        email (EmailStr): The email address of the user requesting the password reset.
    """

    email: EmailStr


class ResetPasswordConfirmSchema(BaseModel):
    """
    Schema for confirming a password reset, containing the new password and token.

    Attributes:
        new_password (str): The new password that the user wants to set.
        token (str): The token received in the password reset email.
    """

    new_password: str
    token: str


class EmailChangeSchema(BaseModel):
    """
    Schema for requesting an email change, containing both old and new email addresses.

    Attributes:
        old_email (EmailStr): The current email address of the user.
        new_email (EmailStr): The new email address the user wants to set.
    """

    old_email: EmailStr
    new_email: EmailStr
