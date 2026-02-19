from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import jwt
from datetime import datetime, timezone

from app.users import repository, schemas, models
from app.core import security
from app.core.config import settings

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

async def refresh_user_token(db: Session, refresh_token: str, redis_client):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        jti: str = payload.get("jti")
        
        if email is None or token_type != "refresh" or jti is None:
            raise credentials_exception
            
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    # Check if refresh token was revoked
    if redis_client:
        is_denylisted = await redis_client.get(f"denylist:{jti}")
        if is_denylisted:
            raise credentials_exception
        
    user = repository.get_user_by_email(db, email=email)
    if not user:
        raise credentials_exception
        
    new_access_token = security.create_access_token(data={"sub": user.email})
    new_refresh_token = security.create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": new_access_token, 
        "refresh_token": new_refresh_token, 
        "token_type": "bearer"
    }

async def denylist_tokens(access_token: str, refresh_token: str, redis_client):
    """Extracts JTI from tokens and adds them to Redis until they expire naturally."""
    if not redis_client:
        return # Skip if Redis is unavailable (e.g., testing)

    tokens_to_revoke = [access_token, refresh_token]
    
    for token in tokens_to_revoke:
        if not token:
            continue
        try:
            # Decode without verifying expiration (we want to revoke it even if it just expired)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
            jti = payload.get("jti")
            exp = payload.get("exp")
            
            if jti and exp:
                # Calculate remaining time in seconds
                now = int(datetime.now(timezone.utc).timestamp())
                expires_in = exp - now
                
                # Only add to Redis if it hasn't completely expired yet
                if expires_in > 0:
                    await redis_client.setex(f"denylist:{jti}", expires_in, "revoked")
                    
        except jwt.InvalidTokenError:
            pass # Malformed tokens can be safely ignored

def update_device_token(db: Session, user: models.User, fcm_token: str):
    return repository.update_fcm_token(db=db, db_user=user, fcm_token=fcm_token)