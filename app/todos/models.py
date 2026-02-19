from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    color = Column(String, default="#000000")
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="categories")
    todos = relationship("Todo", back_populates="category")

class SubTask(Base):
    __tablename__ = "sub_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    
    todo_id = Column(Integer, ForeignKey("todos.id", ondelete="CASCADE"))
    todo = relationship("Todo", back_populates="sub_tasks")

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(Integer, default=3) # 1=High, 2=Medium, 3=Low
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="todos")
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="todos")
    
    sub_tasks = relationship("SubTask", back_populates="todo", cascade="all, delete-orphan")

    # For tracking background notifications
    reminder_time = Column(DateTime(timezone=True), nullable=True)
    notification_sent = Column(Boolean, default=False)