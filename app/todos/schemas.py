from pydantic import BaseModel, ConfigDict
from typing import Optional

# Shared properties
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoCreate(TodoBase):
    pass # Inherits everything from TodoBase without changes

class TodoResponse(TodoBase):
    id: int

    # This tells Pydantic to happily read data even if it's an SQLAlchemy Model
    model_config = ConfigDict(from_attributes=True)