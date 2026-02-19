from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.users import repository, schemas
from app.core import security

def create_user(db: Session, user: schemas.UserCreate):
    db_user = repository.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = security.get_password_hash(user.password)
    
    return repository.create_user(db=db, user=user, hashed_password=hashed_password)

def authenticate_user(db: Session, email: str, password: str):
    user = repository.get_user_by_email(db, email=email)
    if not user:
        return False
    
    if not security.verify_password(password, user.hashed_password):
        return False
        
    return user