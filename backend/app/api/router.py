from fastapi import APIRouter

from app.api import rest_correction, rest_preferences, rest_tts

api_router = APIRouter()

# Register REST endpoints under /api/v1
api_router.include_router(rest_correction.router, tags=["Correction"])
api_router.include_router(rest_tts.router, tags=["TTS"])
api_router.include_router(rest_preferences.router, tags=["Preferences"])
