"""Base classes for data schemas."""
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """Base schema class."""
    model_config = ConfigDict(from_attributes=True)
