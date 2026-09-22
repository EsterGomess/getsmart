"""CRUD operations for the NoteLink model."""
import re

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Note, NoteLink

LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


async def sync_links_for_note(db: AsyncSession, note: Note) -> None:
    """
    Extract [[Title]] markers from note.content and ADD them as outgoing
    links, without touching the links that already exist.

    - Strips the [[...]] markup from the stored content.
    - Never deletes existing NoteLinks.

    Idempotent: re-running with the same (stripped) content does nothing.
    """
    if note.id is None:
        raise ValueError("sync_links_for_note called before note was flushed")

    # 1. Extract titles (lowercased for matching).
    titles = {
        m.strip().lower()
        for m in LINK_RE.findall(note.content)
        if m.strip()
    }

    # 2. Strip the [[Title]] markup and collapse leftover spaces.
    cleaned = LINK_RE.sub("", note.content)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    note.content = cleaned

    # 3. Nothing new to link.
    if not titles:
        return

    # 4. Resolve titles -> IDs (same user, drop self).
    result = await db.execute(
        select(Note.id).where(
            Note.user_id == note.user_id,
            func.lower(Note.title).in_(titles),
        )
    )
    target_ids = {row[0] for row in result if row[0] != note.id}
    if not target_ids:
        return

    # 5. Fetch existing link targets to avoid duplicates.
    existing = await db.execute(
        select(NoteLink.target_note_id).where(
            NoteLink.source_note_id == note.id
        )
    )
    existing_ids = {row[0] for row in existing}

    # 6. Insert only the missing ones.
    for tid in target_ids - existing_ids:
        db.add(NoteLink(source_note_id=note.id, target_note_id=tid))