from pydantic import BaseModel, Field
from typing import List, Optional

class CorrectionRequest(BaseModel):
    text: str = Field(..., description="Raw gesture sequence text classification output")
    context: Optional[List[str]] = Field(default=[], description="List of previous conversation sentences for context")

class CorrectionResponse(BaseModel):
    original: str
    corrected: str
    latency_ms: int

class SynthesizeRequest(BaseModel):
    text: str = Field(..., description="Sentence text to synthesize to speech")
    voice: Optional[str] = Field(default="en-IN-Wavenet-B", description="GCP TTS voice identifier")
    speed: Optional[float] = Field(default=1.0, description="Speed scaling of the speech audio")

class SynthesizeResponse(BaseModel):
    audio_base64: str
    format: str
    duration_ms: int

class PreferencesRequest(BaseModel):
    tts_enabled: Optional[bool] = None
    tts_voice: Optional[str] = None
    tts_speed: Optional[float] = None
    captions_enabled: Optional[bool] = None
    caption_font_size: Optional[str] = None
    sign_detection_enabled: Optional[bool] = None
    overlay_position: Optional[str] = None
    overlay_opacity: Optional[float] = None

class PreferencesResponse(BaseModel):
    tts_enabled: bool
    tts_voice: str
    tts_speed: float
    captions_enabled: bool
    caption_font_size: str
    sign_detection_enabled: bool
    overlay_position: str
    overlay_opacity: float
