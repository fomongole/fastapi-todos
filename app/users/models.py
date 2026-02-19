from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # The device token for push notifications
    fcm_token = Column(String, nullable=True)
    
    todos = relationship("Todo", back_populates="owner")
    categories = relationship("Category", back_populates="owner")