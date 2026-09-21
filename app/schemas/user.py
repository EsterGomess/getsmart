"""Schema for user information."""
from pydantic import SecretStr, Field

from app.schemas.base import BaseSchema

class UserCreateSchema(BaseSchema):
    """Schema for user information."""
    username: str =  Field(examples=["meu_username"])
    password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plan password for the user."
                    "Must be at least 8 characters long "
                    "and contain at least one uppercase letter, "
                    "one lowercase letter, one digit, and one special character.",
        examples=["Mypassword123!"],
    )


class UserResponseCreateSchema(BaseSchema):
    """Schema for user information."""
    username: str = Field(examples=["meu_username"])


class UserLoginSchema(BaseSchema):
    """Schema for user login information."""
    username: str = Field(examples=["meu_username"])
    password: SecretStr = Field(
        examples=["Mypassword123!"]
    )


class UserLoginResponseSchema(BaseSchema):
    """Schema for user login response."""
    username: str = Field(examples=["meu_username"])
    access_token: str = Field(examples=["seu_token_de_acesso"])
    token_type: str = Field(default="bearer", examples=["bearer"])
