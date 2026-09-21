"""Data schemas for authentication."""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token data."""
    username: str | None = None


class UserTokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
