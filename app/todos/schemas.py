from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

# --- CATEGORY SCHEMAS ---
class CategoryBase(BaseModel):
    name: str
    color: Optional[str] = "#000000"

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- SUB-TASK SCHEMAS ---
class SubTaskBase(BaseModel):
    title: str
    is_completed: bool = False

class SubTaskCreate(SubTaskBase):
    pass

class SubTaskResponse(SubTaskBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- TODO SCHEMAS ---
# Shared properties
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: int = Field(default=3, ge=1, le=3, description="1=High, 2=Medium, 3=Low")
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None

class TodoCreate(TodoBase):
    sub_tasks: Optional[List[SubTaskCreate]] = []

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1, le=3)
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None

class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    category: Optional[CategoryResponse] = None
    sub_tasks: List[SubTaskResponse] = []

    # This tells Pydantic to read data even if it's an SQLAlchemy Model
    model_config = ConfigDict(from_attributes=True)

class PaginatedTodoResponse(BaseModel):
    items: List[TodoResponse]
    total: int
    page: int
    size: int
    pages: int