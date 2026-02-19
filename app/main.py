from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend
from redis import asyncio as aioredis

from app.todos.router import router as todos_router
from app.users.router import router as users_router
from app.core.config import settings
from app.core.exceptions import (
    global_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    http_exception_handler,
)

from app.core.worker import process_reminders

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = None

    # --- CACHE INIT ---
    if settings.TESTING:
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
        app.state.redis = None
    else:
        redis = aioredis.from_url(settings.REDIS_URL)
        
        # Verify connection on startup
        try:
            logger.info("Connecting to Redis/Upstash...")
            await redis.ping()
            logger.info("Successfully connected to Redis!")
        except Exception as e:
            logger.error(f"Failed to connect to Redis at {settings.REDIS_URL}: {e}")

        # Attach raw redis to app state for denylist operations
        app.state.redis = redis
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        
        # Start the background reminder worker (Skipped during Pytest)
        asyncio.create_task(process_reminders())
        logger.info("Background Notification Worker Started.")

    yield

    # --- SHUTDOWN ---
    if redis:
        await redis.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="A robust Todo API built with FastAPI and clean architecture.",
    debug=settings.DEBUG_MODE,
    lifespan=lifespan,
)

# --- Rate Limiting (Disable During Tests) ---
if not settings.TESTING:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception Handlers ---
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# --- Routers ---
app.include_router(todos_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "success",
        "message": "Welcome to the Todos API! The server is running perfectly.",
    }