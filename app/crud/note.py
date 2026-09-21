"""CRUD operations for the Note model."""
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.note import Note
from app.schemas import NoteCreateSchema, NoteUpdateSchema


async def get_notes_paginated_by_user(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Note], int]:
    """Fetch a paginated list of notes for a specific user."""
    skip = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count()).select_from(Note).where(Note.user_id == user_id)
    )
    total = total_result.scalar_one()

    result = await db.execute(
        select(Note)
        .where(Note.user_id == user_id)
        .options(selectinload(Note.user))
        .order_by(Note.created_at.desc())
        .offset(skip)
        .limit(page_size)
    )
    notes = list(result.scalars().all())
    return notes, total

async def get_note_by_user_by_id(
    db: AsyncSession,
    note_id: int,
    user_id: int,
) -> Note | None:
    """Fetch a note by its ID and user ID."""
    result = await db.execute(
        select(Note)
        .where(Note.id == note_id, Note.user_id == user_id)
        .options(
            selectinload(Note.user),
            selectinload(Note.outgoing_links),
            selectinload(Note.incoming_links),
        )
    )

    return result.scalar_one_or_none()

async def create_note(
    db: AsyncSession,
    user_id: int,
    payload: NoteCreateSchema,
) -> Note:
    """Create a new note for a specific user."""
    note = Note(
        title=payload.title,
        content=payload.content,
        source=payload.source,
        note_type=payload.note_type,
        user_id=user_id,
    )

    db.add(note)
    await db.commit()
    await db.refresh(note)

    return note

async def update_note(
    db: AsyncSession,
    user_id: int,
    note_id: int,
    payload: NoteUpdateSchema,
) -> Note | None:
    """Updates a note for a specific user. Returns None if the note does not exist."""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    note = result.scalar_one_or_none()
    if note is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    await db.commit()
    await db.refresh(note)
    return note

async def delete_note(db, user_id, note_id) -> Note | None:
    """Deletes a note for a specific user. Returns None if the note does not exist."""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    note = result.scalar_one_or_none()
    if note is None:
        return None
    await db.delete(note)
    await db.commit()
    return note
