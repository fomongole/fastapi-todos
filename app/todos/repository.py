from sqlalchemy.orm import Session
from app.todos import models, schemas

def get_todos(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).filter(models.Todo.owner_id == owner_id).offset(skip).limit(limit).all()

def get_todo_by_id(db: Session, todo_id: int, owner_id: int):
    return db.query(models.Todo).filter(
        models.Todo.id == todo_id, 
        models.Todo.owner_id == owner_id
    ).first()

def create_todo(db: Session, todo: schemas.TodoCreate, owner_id: int):
    # Explicitly add the owner_id
    db_todo = models.Todo(**todo.model_dump(), owner_id=owner_id)
    
    db.add(db_todo)       
    db.commit()           
    db.refresh(db_todo)   
    
    return db_todo

def update_todo(db: Session, db_todo: models.Todo, todo_update: schemas.TodoCreate):
    update_data = todo_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_todo, key, value) 
        
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, db_todo: models.Todo):
    db.delete(db_todo)
    db.commit()