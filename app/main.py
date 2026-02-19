from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from fastapi.middleware.cors import CORSMiddleware
from app.todos.router import router as todos_router
from app.users.router import router as users_router
from app.core.config import settings
from app.core.exceptions import (
    global_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="A robust Todo API built with FastAPI and clean architecture.",
    debug=settings.DEBUG_MODE
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Domain routers
app.include_router(todos_router)
app.include_router(users_router)

# A basic health-check route
@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "success", 
        "message": "Welcome to the Todos API! The server is running perfectly."
    }