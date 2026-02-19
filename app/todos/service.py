from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.todos import repository, schemas

def get_todos(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return repository.get_todos(db=db, owner_id=owner_id, skip=skip, limit=limit)

def get_todo(db: Session, todo_id: int, owner_id: int):
    todo = repository.get_todo_by_id(db=db, todo_id=todo_id, owner_id=owner_id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with ID {todo_id} not found")
    return todo

def create_todo(db: Session, todo: schemas.TodoCreate, owner_id: int):
    return repository.create_todo(db=db, todo=todo, owner_id=owner_id)

def update_todo(db: Session, todo_id: int, todo_update: schemas.TodoUpdate, owner_id: int):
    db_todo = get_todo(db=db, todo_id=todo_id, owner_id=owner_id) 
    return repository.update_todo(db=db, db_todo=db_todo, todo_update=todo_update)

def delete_todo(db: Session, todo_id: int, owner_id: int):
    db_todo = get_todo(db=db, todo_id=todo_id, owner_id=owner_id)
    repository.delete_todo(db=db, db_todo=db_todo)
    return db_todo