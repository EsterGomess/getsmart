"""API Client CRUD operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import APIClient


async def get_api_client_by_username(
    db: AsyncSession,
    username: str,
) -> APIClient | None:
    """
    Get an API client by username.
    :param db: The database session.
    :param username: The username of the API client to retrieve.
    :return: The API client if found, otherwise None.
    """
    result = await db.execute(
        select(APIClient).where(APIClient.username == username)
    )

    return result.scalar_one_or_none()
