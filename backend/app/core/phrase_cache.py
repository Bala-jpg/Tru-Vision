# Static cache maps common gesture outputs/short phrases to corrected sentences
# to bypass Gemini LLM invocation, saving latency and cost.
PHRASE_CACHE = {
    "hello": "Hello.",
    "thank you": "Thank you.",
    "sorry": "Sorry.",
    "need help": "I need help.",
    "water": "Can I have some water, please?",
    "yes": "Yes.",
    "no": "No.",
    "wait": "Please wait.",
    "stop": "Please stop.",
    "meeting": "The meeting is starting.",
    "tomorrow": "Tomorrow.",
    "me join": "I will join.",
    "tomorrow meeting me join": "I will join the meeting tomorrow."
}

def lookup_phrase(phrase: str) -> str | None:
    """
    Looks up a phrase (case-insensitive, trimmed) in the local cache.
    Returns the corrected sentence if matched, else None.
    """
    if not phrase:
        return None
    normalized = phrase.strip().lower()
    return PHRASE_CACHE.get(normalized)
