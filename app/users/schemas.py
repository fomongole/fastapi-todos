from pydantic import BaseModel, EmailStr, ConfigDict

# 1. Base properties shared across schemas
class UserBase(BaseModel):
    email: EmailStr 

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str