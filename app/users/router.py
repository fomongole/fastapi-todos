from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.users import schemas, service, models
from app.users.dependencies import get_current_user
from app.core import security

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Expects standard JSON
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return service.create_user(db=db, user=user)

# Expects Form Data due to OAuth2 standard
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 specifies "username", but we are using emails. 
    # So we pass form_data.username into the email parameter!
    user = service.authenticate_user(db, email=form_data.username, password=form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = security.create_access_token(data={"sub": user.email})
    refresh_token = security.create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    token_data: schemas.TokenRefresh, 
    request: Request,
    db: Session = Depends(get_db)
):
    redis_client = request.app.state.redis
    return await service.refresh_user_token(
        db=db, 
        refresh_token=token_data.refresh_token, 
        redis_client=redis_client
    )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    logout_data: schemas.LogoutRequest, 
    request: Request, 
    current_user: models.User = Depends(get_current_user)
):
    # 1. Extract access token from the request header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid authorization header"
        )
    access_token = auth_header.split(" ")[1]

    # 2. Add both tokens to the Redis denylist
    redis_client = request.app.state.redis
    await service.denylist_tokens(
        access_token=access_token, 
        refresh_token=logout_data.refresh_token, 
        redis_client=redis_client
    )

    return {"message": "Successfully logged out!"}

@router.patch("/device-token", status_code=status.HTTP_200_OK)
def update_device_token(
    token_data: schemas.DeviceTokenUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    service.update_device_token(db=db, user=current_user, fcm_token=token_data.fcm_token)
    return {"message": "Device token updated successfully"}