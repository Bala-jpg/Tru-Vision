import time

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import CorrectionRequest, CorrectionResponse
from app.services.correction_service import CorrectionService

router = APIRouter()


# Dependency provider for CorrectionService
def get_correction_service():
    return CorrectionService()


@router.post("/correct", response_model=CorrectionResponse)
async def correct_phrase(
    payload: CorrectionRequest, service: CorrectionService = Depends(get_correction_service)
):
    """
    POST /api/v1/correct
    Translates raw text signs sequence into a grammatically correct sentence
    using a hybrid local phrase cache + Gemini LLM fallback.
    """
    start_time = time.perf_counter()
    try:
        corrected = await service.correct_sentence(payload.text)
        latency = int((time.perf_counter() - start_time) * 1000)
        return CorrectionResponse(original=payload.text, corrected=corrected, latency_ms=latency)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
