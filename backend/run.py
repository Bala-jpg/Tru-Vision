"""
TruVision Backend — dev entry point.

Usage:
    python run.py              # start with default settings
    uv run python run.py       # start via uv
"""

import uvicorn

from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
