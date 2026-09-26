"""Schemas for the Notes AI service."""
from app.schemas.base import BaseSchema
from pydantic import Field


class SuggestConnectionsRequest(BaseSchema):
    """Request schema for suggesting connections."""
    title: str = Field(..., min_length=1,
                       max_length=255,
                       json_schema_extra={"example": "Example title"}
                       )
    content: str = Field(..., min_length=10,
                         max_length=20_000,
                         json_schema_extra={"example": "Example content"}
                         )


class ConnectionSuggestion(BaseSchema):
    """Schema for a single connection suggestion."""
    title: str = Field(..., min_length=1,
                       max_length=255,
                       json_schema_extra={"example": "Example title"}
                       )
    reason: str = Field(..., min_length=1,
                        max_length=255,
                        json_schema_extra={"example": "Example reason"}
                        )


class SuggestionsSchema(BaseSchema):
    """Schema for connection suggestions."""
    connections: list[ConnectionSuggestion] = Field(default_factory=list)
