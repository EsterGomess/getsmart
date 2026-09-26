"""Integration tests for get_candidate_notes."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import get_candidate_notes
from app.models import Note, NoteType, User


@pytest_asyncio.fixture
async def notes_for_user(db: AsyncSession, user: User) -> list[Note]:
    """Create 5 notes for the user, with distinct created_at."""
    from datetime import datetime, timedelta

    base = datetime(2026, 1, 1, 12, 0, 0)
    notes = []
    for i in range(5):
        n = Note(
            title=f"Note {i}",
            content=f"content {i}",
            note_type=NoteType.FLEETING,
            user_id=user.id,
            created_at=base + timedelta(minutes=i),
        )
        db.add(n)
        notes.append(n)
    await db.commit()
    for n in notes:
        await db.refresh(n)
    return notes


class TestGetCandidateNotes:
    pytestmark = pytest.mark.asyncio

    async def test_returns_notes_for_user(
        self, db: AsyncSession, user: User, notes_for_user: list[Note]
    ):
        result = await get_candidate_notes(db=db, user_id=user.id)
        assert len(result) == 5

    async def test_ordered_by_created_at_desc(
        self, db: AsyncSession, user: User, notes_for_user: list[Note]
    ):
        result = await get_candidate_notes(db=db, user_id=user.id)
        titles = [n.title for n in result]
        assert titles == ["Note 4", "Note 3", "Note 2", "Note 1", "Note 0"]

    async def test_excludes_given_note(
        self, db: AsyncSession, user: User, notes_for_user: list[Note]
    ):
        excluded = notes_for_user[2]  # "Note 2"
        result = await get_candidate_notes(
            db=db, user_id=user.id, exclude_note_id=excluded.id
        )
        assert excluded.id not in [n.id for n in result]
        assert len(result) == 4

    async def test_respects_limit(
        self, db: AsyncSession, user: User, notes_for_user: list[Note]
    ):
        result = await get_candidate_notes(db=db, user_id=user.id, limit=2)
        assert len(result) == 2
        assert [n.title for n in result] == ["Note 4", "Note 3"]

    async def test_isolated_by_user(
        self,
        db: AsyncSession,
        user: User,
        other_user: User,
        notes_for_user: list[Note],
    ):
        # other_user has no notes
        result = await get_candidate_notes(db=db, user_id=other_user.id)
        assert result == []

    async def test_empty_when_user_has_no_notes(self, db: AsyncSession, user: User):
        result = await get_candidate_notes(db=db, user_id=user.id)
        assert result == []
