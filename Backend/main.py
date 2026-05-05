"""
Main application module.
"""
import os
import sys

from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlmodel import SQLModel, create_engine, Session
from starlette.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from logging_config import configure_logging
from scheduler import scheduler

# Configure logging before importing routes so modules inherit handlers
configure_logging()

from routes import acquisition_systems, captures, rooms, user, auth, notifications, eco_game
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from services.limiter import limiter

# Add the project root to sys.path to allow imports from 'database' 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors.
    """
    path = request.url.path
    method = request.method.upper()

    # Keep a specific message for room reactions (like/dislike).
    if path.startswith("/rooms/") and path.endswith(("/like", "/dislike")) and method == "POST":
        return JSONResponse(
            status_code=429,
            content={"detail": "Limite atteinte : 3 réaction maximum par heure"}
        )

    return JSONResponse(
        status_code=429,
        content={"detail": "Limite atteinte : 3 messages maximum par heure"}
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    print("🚀 Starting application...")
    
    # Initialize DB here instead of at module level to avoid import-time crashes
    try:
        init_db()
    except Exception as e:
        print(f"WARNING: DB Initialization failed: {e}")

    # Load seed data
    try:
        from seed_data import seed_data
        seed_data()
    except Exception as e:
        print(f"WARNING: Seed data loading failed: {e}")

    scheduler.start()
    yield
    # Shutdown
    print("🛑 Shutting down application...")
    scheduler.stop()

app = FastAPI(
    title="Sensor Management API",
    description="API for managing IoT sensors and data collection",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

engine = create_engine(settings.DATABASE_URL, echo=True)

origins = [
    "https://sae-n2-projet-capteurs-3b45b3.forge-pages.iut-larochelle.fr",
    "https://but2-2-backprod.cleverapps.io",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # credentials are allowed because of authentification
    allow_methods=["*"], # We officialy use only these 4
    allow_headers=["*"], # Authorization for authentication tokens and content-type for request bodies
)


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(rooms.router)
app.include_router(captures.router)
app.include_router(notifications.router)
app.include_router(acquisition_systems.router)
app.include_router(eco_game.router)


@app.get("/")
def read_root():
    """
    Root endpoint.
    """
    return {"Hello": "World"}


@app.get("/fix_db_schema")
def fix_db_schema():
    """
    Fix the database schema by adding missing columns and constraints.
    """
    from sqlalchemy.exc import SQLAlchemyError

    with Session(engine) as session:
        try:
            session.exec(text('ALTER TABLE capture ADD COLUMN "AS_name" VARCHAR(50);')) # add missing column
            session.exec(text('ALTER TABLE capture ADD CONSTRAINT fk_capture_as FOREIGN KEY ("AS_name") REFERENCES automated_systems(name);')) # add missing foreign key constraint
            session.commit()
            return {"message": "Schema updated"}
        except SQLAlchemyError as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.exception("Error updating DB schema")
            return {"message": f"Error (maybe column exists): {e}"}


# Include routers
app.include_router(rooms.router)
app.include_router(acquisition_systems.router)
app.include_router(captures.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(notifications.router)
app.include_router(eco_game.router)

