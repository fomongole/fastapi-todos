from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.todos import schemas, service

from app.users.dependencies import get_current_user
from app.users.models import User

from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)

@router.post("/", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: schemas.TodoCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await FastAPICache.clear(namespace="todos")
    return service.create_todo(db=db, todo=todo, owner_id=current_user.id)

@router.get("/", response_model=schemas.PaginatedTodoResponse)
@cache(expire=60, namespace="todos") # Cache for 1 minute
async def read_todos(
    page: int = 1, 
    size: int = 10,
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items, total = service.get_todos(
        db=db, 
        owner_id=current_user.id, 
        page=page, 
        size=size,
        completed=completed,
        priority=priority,
        search=search
    )
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size if total > 0 else 0
    }

@router.get("/{todo_id}", response_model=schemas.TodoResponse)
def read_todo(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_todo(db=db, todo_id=todo_id, owner_id=current_user.id)

@router.patch("/{todo_id}", response_model=schemas.TodoResponse)
async def update_todo(
    todo_id: int, 
    todo_update: schemas.TodoUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await FastAPICache.clear(namespace="todos")
    return service.update_todo(db=db, todo_id=todo_id, todo_update=todo_update, owner_id=current_user.id)

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await FastAPICache.clear(namespace="todos")
    service.delete_todo(db=db, todo_id=todo_id, owner_id=current_user.id)