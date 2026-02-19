from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.todos import repository, schemas

def get_categories(db: Session, owner_id: int):
    return repository.get_categories(db=db, owner_id=owner_id)

def get_category(db: Session, category_id: int, owner_id: int):
    category = repository.get_category_by_id(db=db, category_id=category_id, owner_id=owner_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    return category

def create_category(db: Session, category: schemas.CategoryCreate, owner_id: int):
    return repository.create_category(db=db, category=category, owner_id=owner_id)

def update_category(db: Session, category_id: int, category_update: schemas.CategoryUpdate, owner_id: int):
    db_category = get_category(db=db, category_id=category_id, owner_id=owner_id)
    return repository.update_category(db=db, db_category=db_category, category_update=category_update)

def delete_category(db: Session, category_id: int, owner_id: int):
    db_category = get_category(db=db, category_id=category_id, owner_id=owner_id)
    repository.delete_category(db=db, db_category=db_category)
    return db_category

def get_todos(
    db: Session, 
    owner_id: int, 
    page: int = 1, 
    size: int = 10,
    completed: bool | None = None,
    priority: int | None = None,
    search: str | None = None
):
    items = repository.get_todos(
        db=db, owner_id=owner_id, page=page, size=size,
        completed=completed, priority=priority, search=search
    )
    total = repository.get_todos_count(
        db=db, owner_id=owner_id, 
        completed=completed, priority=priority, search=search
    )
    return items, total

def get_todo(db: Session, todo_id: int, owner_id: int):
    todo = repository.get_todo_by_id(db=db, todo_id=todo_id, owner_id=owner_id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with ID {todo_id} not found")
    return todo

def create_todo(db: Session, todo: schemas.TodoCreate, owner_id: int):
    
    if todo.category_id is not None:
        get_category(db=db, category_id=todo.category_id, owner_id=owner_id)
        
    return repository.create_todo(db=db, todo=todo, owner_id=owner_id)

def update_todo(db: Session, todo_id: int, todo_update: schemas.TodoUpdate, owner_id: int):
    db_todo = get_todo(db=db, todo_id=todo_id, owner_id=owner_id) 
    
    if todo_update.category_id is not None:
        get_category(db=db, category_id=todo_update.category_id, owner_id=owner_id)
        
    return repository.update_todo(db=db, db_todo=db_todo, todo_update=todo_update)

def delete_todo(db: Session, todo_id: int, owner_id: int):
    db_todo = get_todo(db=db, todo_id=todo_id, owner_id=owner_id)
    repository.delete_todo(db=db, db_todo=db_todo)
    return db_todo