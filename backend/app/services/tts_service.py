import base64

from app.config import settings

try:
    from google.cloud import texttospeech
except ImportError:
    texttospeech = None


class TTSService:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        # Initialize Google TTS client only if credentials/keys are configured
        if self._client is None and texttospeech is not None:
            if settings.GOOGLE_APPLICATION_CREDENTIALS or settings.GOOGLE_TTS_KEY:
                try:
                    self._client = texttospeech.TextToSpeechClient()
                except Exception as e:
                    print(f"Failed to initialize Google Cloud TTS client: {e}")
        return self._client

    async def synthesize(
        self, text: str, voice_name: str = "en-IN-Wavenet-B", speed: float = 1.0
    ) -> tuple[str, str]:
        """
        Synthesizes text to speech.
        Returns a tuple of (audio_base64_string, format_extension).
        If Google TTS credentials are not configured, returns a mock/silence placeholder for early setup testing.
        """
        if not text or not text.strip():
            return "", "mp3"

        client = self.client
        if not client:
            print("Google TTS not configured. Returning mock audio base64 payload.")
            # A tiny 1-second silent MP3 base64 so extension playback doesn't throw errors during local setup
            mock_mp3_base64 = (
                "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGFtZTMuMTAwZXJyb3IAAAAAAAAAAAAAAA"
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                "//uQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            )
            return mock_mp3_base64, "mp3"

        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Select the voice parameters
            language_code = "-".join(voice_name.split("-")[:2])  # e.g. en-IN
            voice = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)

            # Select the type of audio file you want returned
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=speed
            )

            # Perform the text-to-speech request
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                ),
            )

            # Base64 encode the binary audio content
            audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")
            return audio_base64, "mp3"

        except Exception as e:
            print(f"Google Cloud TTS call failed: {e}")
            raise e
