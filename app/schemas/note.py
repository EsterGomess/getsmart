"""Note schemas."""
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.note import NoteType
from app.schemas.base import BaseSchema


class NoteReadSchema(BaseSchema):
    """Schema for reading a note."""
    id: int
    title: str
    content: str
    source: str | None
    note_type: NoteType
    user_id: int
    created_at: datetime
    updated_at: datetime


class NotesPageSchema(BaseSchema):
    """Schema for paginated notes."""
    items: list[NoteReadSchema]
    total: int
    page: int
    page_size: int
    pages: int


class NoteLinkReadSchema(BaseSchema):
    """Schema for reading a note link."""
    id: int
    source_note_id: int
    target_note_id: int


class NoteReadDetailedSchema(BaseSchema):
    """Schema for reading a note with its links."""
    id: int
    title: str
    content: str
    source: str | None
    note_type: NoteType
    user_id: int
    created_at: datetime
    updated_at: datetime
    outgoing_links: list[NoteLinkReadSchema] = []
    incoming_links: list[NoteLinkReadSchema] = []


class NoteCreateSchema(BaseModel):
    """Payload for creating a note."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    source: str | None = Field(None, max_length=255)
    note_type: NoteType = NoteType.FLEETING


class NoteUpdateSchema(BaseModel):
    """Payload for updating a note. All fields are optional."""
    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = Field(None, min_length=1)
    source: str | None = Field(None, max_length=255)
    note_type: NoteType | None = None
