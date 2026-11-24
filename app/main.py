
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database.connection import Base, engine
from app.models.transcription import Transcription
from app.api.transcription import router as transcription_router
from app.api.speech import router as speech_router


# Create database tables
Base.metadata.create_all(bind=engine)


# Initialize FastAPI application
app = FastAPI(
    title="Real-Time Multilingual Speech-to-Text",
    description="AI-powered multilingual speech transcription platform",
    version="1.0.0"
)


# Register API routers
app.include_router(transcription_router)
app.include_router(speech_router)


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Speech-to-Text"
    }


# Serve frontend
app.mount(
    "/",
    StaticFiles(directory="app/static", html=True),
    name="static"
)
