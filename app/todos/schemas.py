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

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1, le=3)
    due_date: Optional[datetime] = None

class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)