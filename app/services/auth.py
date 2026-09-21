from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.api_client import get_api_client_by_username
from app.crud.user import get_user_by_username
from app.models import APIClient, User
from app.core.security import verify_password


async def authenticate_api_client(
    db: AsyncSession,
    username: str,
    password: str,
) -> APIClient | None:

    api_client = await get_api_client_by_username(
        db=db,
        username=username,
    )

    if api_client is None:
        return None

    if not verify_password(
        password,
        api_client.hashed_password,
    ):
        return None

    return api_client


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,
) -> User | None:

    user = await get_user_by_username(
        db=db,
        username=username,
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    return user