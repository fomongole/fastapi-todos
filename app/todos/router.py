from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.todos import schemas, service

from app.users.dependencies import get_current_user
from app.users.models import User

from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from app.core.cache import custom_key_builder

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)

# --- CATEGORY ENDPOINTS ---
@router.post("/categories", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED, tags=["Categories"])
async def create_category(
    category: schemas.CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.create_category(db=db, category=category, owner_id=current_user.id)

@router.get("/categories", response_model=List[schemas.CategoryResponse], tags=["Categories"])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_categories(db=db, owner_id=current_user.id)

@router.get("/categories/{category_id}", response_model=schemas.CategoryResponse, tags=["Categories"])
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_category(db=db, category_id=category_id, owner_id=current_user.id)

@router.patch("/categories/{category_id}", response_model=schemas.CategoryResponse, tags=["Categories"])
async def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Clear the todos cache because a category color/name update affects cached Todo data!
    await FastAPICache.clear(namespace="todos")
    return service.update_category(db=db, category_id=category_id, category_update=category_update, owner_id=current_user.id)

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Categories"])
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await FastAPICache.clear(namespace="todos")
    service.delete_category(db=db, category_id=category_id, owner_id=current_user.id)

# --- TODO ENDPOINTS ---
@router.post("/", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: schemas.TodoCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await FastAPICache.clear(namespace="todos")
    return service.create_todo(db=db, todo=todo, owner_id=current_user.id)

@router.get("/", response_model=schemas.PaginatedTodoResponse)
@cache(expire=60, namespace="todos", key_builder=custom_key_builder) # Cache for 1 minute
async def read_todos(
    request: Request,
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
    
    # We parse the raw SQLAlchemy models into safe Pydantic models 
    # BEFORE they hit the cache decorator to prevent DetachedInstance errors.
    parsed_items = [schemas.TodoResponse.model_validate(item) for item in items]
    
    return {
        "items": parsed_items,
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