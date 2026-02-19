from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

# 1. Pydantic Validation Handler: Triggered when schemas don't match input
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation failed for {request.method} {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Unprocessable Entity",
            "message": "The data you sent is invalid.",
            "details": exc.errors()
        },
    )

# 2. SQLAlchemy Handler: Triggered when the database acts up
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    # Bind context to the logger so we know which URL failed
    logger.bind(path=request.url.path).error(f"Database error: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "A database operation failed. Check server logs."
        },
    )

# 3. Global Safety Net: Catch-all for logic bugs (e.g., ZeroDivisionError)
async def global_exception_handler(request: Request, exc: Exception):
    # .exception() prints the RED color-coded traceback
    logger.exception("CRITICAL: An unhandled exception escaped the service layer!") 
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error", 
            "message": "An unexpected error occurred. We have been notified."
        }
    )