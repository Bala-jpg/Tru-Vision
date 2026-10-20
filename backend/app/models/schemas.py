from pydantic import BaseModel, Field


class CorrectionRequest(BaseModel):
    text: str = Field(..., description="Raw gesture sequence text classification output")
    context: list[str] | None = Field(
        default=[], description="List of previous conversation sentences for context"
    )


class CorrectionResponse(BaseModel):
    original: str
    corrected: str
    latency_ms: int


class SynthesizeRequest(BaseModel):
    text: str = Field(..., description="Sentence text to synthesize to speech")
    voice: str | None = Field(default="en-IN-Wavenet-B", description="GCP TTS voice identifier")
    speed: float | None = Field(default=1.0, description="Speed scaling of the speech audio")


class SynthesizeResponse(BaseModel):
    audio_base64: str
    format: str
    duration_ms: int


class PreferencesRequest(BaseModel):
    tts_enabled: bool | None = None
    tts_voice: str | None = None
    tts_speed: float | None = None
    captions_enabled: bool | None = None
    caption_font_size: str | None = None
    sign_detection_enabled: bool | None = None
    overlay_position: str | None = None
    overlay_opacity: float | None = None


class PreferencesResponse(BaseModel):
    tts_enabled: bool
    tts_voice: str
    tts_speed: float
    captions_enabled: bool
    caption_font_size: str
    sign_detection_enabled: bool
    overlay_position: str
    overlay_opacity: float
