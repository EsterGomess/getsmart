"""
Authentication service for the FastAPI application.
This module contains functions for user authentication.
"""

from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models import User
from app.schemas import UserCreateSchema, UserLoginSchema
from app.core.security import get_password_hash, verify_password
from app.crud.user import create_user, get_user_by_username

logger = structlog.get_logger()


async def login_user(db: AsyncSession, payload: UserLoginSchema) -> User|None:
    """
    Authenticate a user.
    :param db: The database session.
    :param payload: The user login payload.
    :return: The authenticated user.
    """
    user = await get_user_by_username(db, payload.username)

    if user is None:
        return None

    if not verify_password(payload.password.get_secret_value(), user.hashed_password):
        return None
    return user


async def register_user(db: AsyncSession, payload: UserCreateSchema) -> User | bool:
    """
    Register a new user.
    :param db: The database session.
    :param payload: The user creation payload.
    :return: The created user.
    """
    user = await get_user_by_username(db, payload.username)

    if user:
        return False

    hashed_password = get_password_hash(
        payload.password.get_secret_value()
    )
    user = await create_user(db, payload.username, hashed_password)
    logger.info("User registered successfully", user_id=user.id)
    return user
