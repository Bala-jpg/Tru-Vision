# Try loading faster-whisper gracefully
try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None


class SpeechService:
    def __init__(self):
        self.model: object | None = None
        self.model_size = "base"
        self.load_model()

    def load_model(self):
        if WhisperModel is None:
            print("faster-whisper not installed. Running in speech recognition mock mode.")
            return

        try:
            # Load whisper model in CPU mode, int8 compute type for speed
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            print(f"Loaded faster-whisper '{self.model_size}' model successfully.")
        except Exception as e:
            print(f"Failed to load faster-whisper model: {e}")

    async def transcribe_chunk(self, audio_data: bytes) -> str:
        """
        Transcribes incoming PCM raw audio bytes (expected 16kHz mono).
        Returns string transcription.
        """
        if not audio_data:
            return ""

        if self.model is None:
            # Mock return for testing websocket flow
            return "[Transcribing audio chunk...]"

        try:
            # Convert raw PCM bytes to numpy float32 normalized audio array
            import numpy as np

            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Run transcription (run in executor for async compatibility)
            import asyncio

            loop = asyncio.get_event_loop()

            def run_whisper():
                segments, info = self.model.transcribe(audio_np, beam_size=5)
                text = " ".join([segment.text for segment in segments])
                return text.strip()

            text = await loop.run_in_executor(None, run_whisper)
            return text
        except Exception as e:
            print(f"Speech transcription error: {e}")
            return ""
