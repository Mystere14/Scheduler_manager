import os
import sys

from routes import analyticsTimeslot, lesson
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import create_engine

from config import settings
from database import initDb
from starlette.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    print("🚀 Starting application...")
    try:
        initDb()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ ERROR: DB Initialization failed: {e}")
        raise

    yield
    
    # Shutdown
    print("🛑 Shutting down application...")


app = FastAPI(
    title="Scheduler Manager API",
    description="API for managing scheduling and absences",
    version="1.0.0",
    lifespan=lifespan
)


# Create engine
engine = create_engine(settings.DATABASEURL, echo=True)

# CORS configuration - Include Tauri app origins
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "tauri://localhost",
    "http://tauri.localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(lesson.router)
app.include_router(analyticsTimeslot.router)

@app.get("/")
def readRoot():
    """Root endpoint"""
    return {
        "message": "Scheduler Manager API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def healthCheck():
    """Health check endpoint"""
    return {"status": "healthy"}


