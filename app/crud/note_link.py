"""CRUD operations for the NoteLink model."""
import re
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Note, NoteLink

LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


async def sync_links_for_note(db: AsyncSession, note: Note) -> None:
    """
    Synchronize the links for a given note.
    This function extracts titles from the note's
    content and updates the NoteLink table accordingly."""
    if note.id is None:
        raise ValueError("sync_links_for_note called before note was flushed")

    titles = {
        m.strip().lower()
        for m in LINK_RE.findall(note.content)
        if m.strip()
    }

    target_ids: list[int] = []
    if titles:
        result = await db.execute(
            select(Note.id).where(
                Note.user_id == note.user_id,
                func.lower(Note.title).in_(titles),
            )
        )
        target_ids = list({row[0] for row in result if row[0] != note.id})

    await db.execute(
        delete(NoteLink).where(NoteLink.source_note_id == note.id)
    )

    for tid in target_ids:
        db.add(NoteLink(source_note_id=note.id, target_note_id=tid))