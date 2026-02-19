from sqlalchemy.orm import Session
from sqlalchemy import or_ 
from app.todos import models, schemas

def get_todos(
    db: Session, 
    owner_id: int, 
    page: int = 1, 
    size: int = 10,
    completed: bool | None = None,
    priority: int | None = None,
    search: str | None = None
):
    # The base query (always filter by owner)
    query = db.query(models.Todo).filter(models.Todo.owner_id == owner_id)
    
    # Apply filters if provided
    if completed is not None:
        query = query.filter(models.Todo.completed == completed)
        
    if priority is not None:
        query = query.filter(models.Todo.priority == priority)
        
    # Apply the search query (case-insensitive)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Todo.title.ilike(search_term),
                models.Todo.description.ilike(search_term)
            )
        )
        
    # Calculate offset based on page and apply pagination
    skip = (page - 1) * size
    return query.offset(skip).limit(size).all()

def get_todos_count(
    db: Session, 
    owner_id: int, 
    completed: bool | None = None,
    priority: int | None = None,
    search: str | None = None
):
    query = db.query(models.Todo).filter(models.Todo.owner_id == owner_id)
    if completed is not None:
        query = query.filter(models.Todo.completed == completed)
    if priority is not None:
        query = query.filter(models.Todo.priority == priority)
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(models.Todo.title.ilike(search_term), models.Todo.description.ilike(search_term)))
    return query.count()

def get_todo_by_id(db: Session, todo_id: int, owner_id: int):
    return db.query(models.Todo).filter(
        models.Todo.id == todo_id, 
        models.Todo.owner_id == owner_id
    ).first()

def create_todo(db: Session, todo: schemas.TodoCreate, owner_id: int):
    db_todo = models.Todo(**todo.model_dump(), owner_id=owner_id)
    db.add(db_todo)       
    db.commit()           
    db.refresh(db_todo)   
    return db_todo

def update_todo(db: Session, db_todo: models.Todo, todo_update: schemas.TodoUpdate):
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value) 
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, db_todo: models.Todo):
    db.delete(db_todo)
    db.commit()