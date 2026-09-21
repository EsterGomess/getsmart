""" this script is used to create an APIClient in the database. """
import asyncio

from sqlalchemy import select

from app.core.security import get_password_hash
from app.database import SESSION_LOCAL
from app.models import APIClient

async def create_api_client():
    """Create an APIClient in the database."""
    async with SESSION_LOCAL() as db:
        result = await db.execute(
            select(APIClient).where(APIClient.username == "admin")
        )

        existing_client = result.scalar_one_or_none()

        if existing_client:
            print("APIClient already exists.")
            return

        api_client = APIClient(
            username="admin",
            hashed_password=get_password_hash("admin"),
            is_active=True)

        db.add(api_client)

        await db.commit()
        await db.refresh(api_client)

        print(f"APIClient created: {api_client.username}")


if __name__ == "__main__":
    asyncio.run(create_api_client())
