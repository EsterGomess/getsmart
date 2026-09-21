"""
CRUD operations for the User model.
This module contains functions for performing CRUD operations on the User model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """
    Get a user by their username.
    :param db: The database session.
    :param username: The user's username.
    :return: The user if found, otherwise None.
    """
    statement = select(User).where(User.username == username)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, username: str, hashed_password: str) -> User:
    """
    Create a new user in the database.
    :param db: The database session.
    :param username: The user's username.
    :param hashed_password: The user's hashed password.
    :return: The created user.
    """
    user = User(
            username=username,
            hashed_password=hashed_password,
        )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_registered_user(db: AsyncSession, username: str, hashed_password: str) -> User | None:
    """
    Get a registered user by their username and hashed password.
    :param db: The database session.
    :param username: The user's username.
    :param hashed_password: The user's hashed password.
    :return: The user if found, otherwise None.
    """
    statement = select(User).where(User.username == username,
                                   User.hashed_password == hashed_password)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Get a user by their ID.
    :param db: The database session.
    :param user_id: The user's ID.
    :return: The user if found, otherwise None.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

