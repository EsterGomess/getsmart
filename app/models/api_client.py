"""
This module defines the APIClient model, which represents an API client in the database.
The APIClient model includes fields for username, hashed password,
creation timestamp, active status, and a foreign key relationship to the Contact model.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.authenticatedentity import AuthenticatedEntity

class APIClient(AuthenticatedEntity):
    """Represents an API client in the database."""
    __tablename__ = "api_clients"

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
