import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ws_sign, ws_speech
from app.api.router import api_router
from app.config import settings

app = FastAPI(
    title="TruVision Backend API",
    description="Real-time sign language recognition, sentence correction, and TTS translation backend.",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Add CORS Middleware to enable connections from the Chrome Extension context
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Extension context origins (chrome-extension://*)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register versioned REST endpoints
app.include_router(api_router, prefix="/api/v1")

# Mount WebSocket endpoints directly onto main app for clean URL namespaces
app.include_router(ws_sign.router)
app.include_router(ws_speech.router)


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for container/VM status monitoring.
    """
    return {
        "status": "healthy",
        "version": app.version,
        "services": {
            "gemini_api": "configured" if settings.GEMINI_API_KEY else "unconfigured",
            "supabase_cloud": "configured" if settings.SUPABASE_URL else "unconfigured",
        },
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
