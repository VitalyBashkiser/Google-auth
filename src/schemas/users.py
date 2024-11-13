from pydantic import BaseModel, EmailStr

from src.utils import auth_jwt


class UserBase(BaseModel):
    """
    Base schema for user data containing templates and password fields.

    Attributes:
        email (EmailStr): The user's templates address.
        password (str): The user's plain text password.
    """

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema for representing user data in API responses.

    Attributes:
        id (int): The unique identifier of the user.
        email (EmailStr): The user's templates address.
    """

    id: int
    email: EmailStr


class SchemeLoginUser(UserBase):
    """
    Schema for user login, inheriting from UserBase.

    Inherits:
        templates (EmailStr): User's templates.
        password (str): User's password.
    """

    pass


class SchemeRegisterUser(UserBase):
    """
    Schema for user registration, with additional functionality for hashing the password.

    Methods:
        model_dump: Overrides BaseModel method to hash the password before storing.

    Inherits:
        templates (EmailStr): User's templates.
        password (str): User's password.
    """

    def model_dump(self, *args, **kwargs):
        """
        Generate a dictionary representation of the model with hashed password.

        Returns:
            dict: Model data with hashed password field.
        """
        data = super().model_dump(*args, **kwargs)
        data["hashed_password"] = auth_jwt.hash_password(data.pop("password"))
        return data


class UserInDB(UserBase):
    """
    Schema representing user data in the database, extending basic user fields with additional status fields.

    Attributes:
        id (int): Unique identifier of the user.
        is_active (bool): Status indicating if the user is active.
        is_email_confirmed (bool): Status indicating if the user's templates is confirmed.

    Inherits:
        templates (EmailStr): User's templates.
        password (str): User's password.
    """

    id: int
    is_active: bool
    is_email_confirmed: bool

    class Config:
        """
        Configuration class to enable ORM mode and attribute access.
        """

        from_attributes = True


class SchemeConfirmRegistration(BaseModel):
    """
    Schema for confirming user registration.

    Attributes:
        token (str): The token used for registration confirmation.
    """

    token: str
