"""Service for managing notes."""
from math import ceil

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from starlette import status

from app.crud import (
    get_notes_paginated_by_user,
    get_note_by_user_by_id,
    create_note,
    update_note,
    delete_note
)
from app.schemas import (
    NoteCreateSchema,
    NoteReadSchema,
    NoteUpdateSchema,
)

logger = structlog.get_logger()


async def list_notes_by_user(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 20
):
    """
    List notes for a specific user with pagination.
    :param db: The payload base session.
    :param user_id: The ID of the user.
    :param page: The page number (default is 1).
    :param page_size: The number of notes per page (default is 20).
    :return: A tuple containing the list of notes and the total count.
    """
    logger.info("listing_notes", user_id=user_id, page=page, page_size=page_size)

    notes, total = await get_notes_paginated_by_user(db, user_id, page, page_size)

    return {
        "items": notes,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": ceil(total / page_size) if total else 0,
    }


async def get_note_for_user(db: AsyncSession, user_id: int, note_id: int):
    """
    Get a specific note for a user by note ID.
    :param db: The payload base session.
    :param user_id: The ID of the user.
    :param note_id: The ID of the note.
    :return: The note if found, otherwise None.
    """
    logger.info("fetching_note", user_id=user_id, note_id=note_id)
    note = await get_note_by_user_by_id(
        db=db, user_id=user_id, note_id=note_id
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    return note


async def create_note_for_user(
        db: AsyncSession,
        user_id: int,
        payload: NoteCreateSchema,
) -> NoteReadSchema:
    """
    Create a new note for a specific user.
    :param db: The payload base session.
    :param user_id: The ID of the user.
    :param payload: The note creation payload.
    :return: The created note."""
    logger.info("creating_note", user_id=user_id, title=payload.title)

    note = await create_note(db=db, user_id=user_id, payload=payload)

    logger.info("note_created", user_id=user_id, note_id=note.id)
    return NoteReadSchema.model_validate(note)


async def update_note_for_user(
        db: AsyncSession,
        user_id: int,
        note_id: int,
        payload: NoteUpdateSchema,
) -> NoteReadSchema:
    """
    Update an existing note for a specific user.
    :param db: The payload base session.
    :param user_id: The ID of the user.
    :param note_id: The ID of the note to update.
    :param payload: The note update payload.
    :return: The updated note."""
    logger.info("updating_note", user_id=user_id, note_id=note_id)

    note = await update_note(
        db=db,
        user_id=user_id,
        note_id=note_id,
        payload=payload,
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    logger.info("note_updated", user_id=user_id, note_id=note.id)
    return NoteReadSchema.model_validate(note)

async def delete_note_for_user(
    db: AsyncSession,
    user_id: int,
    note_id: int,
) -> None:
    """Deletes a note for a user or raises 404 if not found."""
    logger.info("deleting_note", user_id=user_id, note_id=note_id)

    note = await delete_note(db=db, user_id=user_id, note_id=note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    logger.info("note_deleted", user_id=user_id, note_id=note_id)
    return None
