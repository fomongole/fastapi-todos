import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.users import repository, models

# This tells FastAPI where the login endpoint is, so it knows how to configure the Swagger UI!
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        jti: str = payload.get("jti")
        
        # Enforce that only 'access' tokens can be used for standard authentication
        if email is None or token_type != "access" or jti is None:
            raise credentials_exception
            
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    # Check if token is denylisted in Redis
    redis = request.app.state.redis
    if redis:
        is_denylisted = await redis.get(f"denylist:{jti}")
        if is_denylisted:
            raise credentials_exception
        
    user = repository.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
        
    return user