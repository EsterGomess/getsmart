"""Create an API client using credentials provided at runtime."""

import asyncio
import getpass
import os
import sys

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import get_password_hash
from app.database import SESSION_LOCAL
from app.models import APIClient


MIN_PASSWORD_LENGTH = 16
MAX_USERNAME_LENGTH = 100


def get_credentials() -> tuple[str, str]:
    """Read credentials from the environment or prompt without echoing secrets."""
    username = os.getenv("API_CLIENT_USERNAME")
    if username is None:
        username = input("API client username: ")
    username = username.strip()

    password = os.getenv("API_CLIENT_PASSWORD")
    if password is None:
        password = getpass.getpass("API client password (min. 16 characters): ")
        password_confirmation = getpass.getpass("Confirm API client password: ")
        if password != password_confirmation:
            raise ValueError("The password confirmation does not match.")

    if not username:
        raise ValueError("The API client username cannot be empty.")
    if len(username) > MAX_USERNAME_LENGTH:
        raise ValueError(
            f"The API client username must be at most {MAX_USERNAME_LENGTH} characters."
        )
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"The API client password must contain at least {MIN_PASSWORD_LENGTH} characters."
        )

    return username, password


async def create_api_client(username: str, password: str) -> None:
    """Create one active API client; never reset or replace an existing client."""
    async with SESSION_LOCAL() as db:
        result = await db.execute(
            select(APIClient).where(APIClient.username == username)
        )
        if result.scalar_one_or_none() is not None:
            raise ValueError(f"An API client named '{username}' already exists.")

        api_client = APIClient(
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True,
        )
        db.add(api_client)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError(
                f"An API client named '{username}' already exists."
            ) from exc

    print(f"API client '{username}' created.")


async def main() -> None:
    username, password = get_credentials()
    await create_api_client(username, password)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ValueError, EOFError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
