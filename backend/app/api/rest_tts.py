from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import SynthesizeRequest, SynthesizeResponse
from app.services.tts_service import TTSService

router = APIRouter()


def get_tts_service():
    return TTSService()


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_text(
    payload: SynthesizeRequest, service: TTSService = Depends(get_tts_service)
):
    """
    POST /api/v1/synthesize
    Generates vocal MP3 audio using Google Cloud TTS.
    Returns base64 encoded audio playable in the browser extension.
    """
    try:
        audio_base64, fmt = await service.synthesize(
            text=payload.text, voice_name=payload.voice, speed=payload.speed
        )
        return SynthesizeResponse(
            audio_base64=audio_base64,
            format=fmt,
            duration_ms=0,  # Streamed duration calculated on client playback
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")
