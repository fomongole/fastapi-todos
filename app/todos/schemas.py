from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

# Shared properties
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    
    priority: int = Field(default=3, ge=1, le=3, description="1=High, 2=Medium, 3=Low")
    due_date: Optional[datetime] = None

class TodoCreate(TodoBase):
    pass # Inherits everything from TodoBase

class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # This tells Pydantic to happily read data even if it's an SQLAlchemy Model
    model_config = ConfigDict(from_attributes=True)