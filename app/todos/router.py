from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.todos import schemas, service

from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)

@router.post("/", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo: schemas.TodoCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.create_todo(db=db, todo=todo, owner_id=current_user.id)

@router.get("/", response_model=List[schemas.TodoResponse])
def read_todos(
    skip: int = 0, 
    limit: int = 100, 
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_todos(
        db=db, 
        owner_id=current_user.id, 
        skip=skip, 
        limit=limit,
        completed=completed,
        priority=priority,
        search=search
    )

@router.get("/{todo_id}", response_model=schemas.TodoResponse)
def read_todo(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_todo(db=db, todo_id=todo_id, owner_id=current_user.id)

@router.patch("/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(
    todo_id: int, 
    todo_update: schemas.TodoUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.update_todo(db=db, todo_id=todo_id, todo_update=todo_update, owner_id=current_user.id)

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service.delete_todo(db=db, todo_id=todo_id, owner_id=current_user.id)