try:
    import google.generativeai as genai
except ImportError:
    genai = None

from app.config import settings
from app.core.phrase_cache import lookup_phrase

# Initialize Gemini if API key is provided
if genai and settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


class CorrectionService:
    def __init__(self):
        self.model_name = "gemini-1.5-flash"
        self._model = None

    @property
    def model(self):
        if self._model is None and genai and settings.GEMINI_API_KEY:
            self._model = genai.GenerativeModel(self.model_name)
        return self._model

    async def correct_sentence(self, raw_text: str) -> str:
        """
        Corrects a raw classified sign text sequence to grammatically correct English.
        Utilizes a hybrid correction pipeline:
        1. Checks local static phrase cache for matching key phrases (0ms LLM latency).
        2. Falls back to Gemini Flash API for sentence correction.
        """
        if not raw_text or not raw_text.strip():
            return ""

        # Step 1: Check cache
        cached = lookup_phrase(raw_text)
        if cached:
            return cached

        # Step 2: Fallback to Gemini LLM
        if not genai or not settings.GEMINI_API_KEY:
            # Local fallback format if no API key is loaded
            return raw_text.capitalize() + "."

        prompt = (
            "You are a translation assistant for Indian Sign Language (ISL). "
            "You will be given a sequence of words produced by gesture classification models. "
            "Your task is to rephrase these words into a natural, grammatically correct English sentence "
            "without adding any extra conversational filler, greeting, or meta-commentary. "
            "Only output the corrected sentence.\n\n"
            f"Words: {raw_text}\n"
            "Corrected:"
        )

        try:
            # We run in executor for async compatibility if calling sync libraries
            # google-generativeai is synchronous under the hood for generate_content
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt, generation_config={"temperature": 0.1, "max_output_tokens": 64}
                ),
            )
            return response.text.strip()
        except Exception as e:
            # Graceful fallback on API issues
            print(f"Gemini API correction failed: {e}")
            return raw_text.capitalize() + "."
