from datetime import datetime

from sqlalchemy import String, func, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class AuthenticatedEntity(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def get_id(self):
        """
        Get the user's ID.
        :return: The user's ID.
        """
        return self.id

    def get_hashed_password(self):
        """
        Get the user's hashed password.
        :return: The user's hashed password.
        """
        return self.hashed_password

    def get_updated_at(self):
        """
        Get the timestamp of when the user was last updated.
        :return: The timestamp of when the user was last updated.
        """
        return self.updated_at

    def get_created_at(self):
        """
        Get the timestamp of when the user was created.
        :return: The timestamp of when the user was created.
        """
        return self.created_at
