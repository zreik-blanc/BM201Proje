import asyncio
from faster_whisper import WhisperModel
from typing import Optional, Any

TTS_MODEL: Optional[Any] = None

WHISPER_MODEL: Optional[WhisperModel] = None

MODEL_LOCK = asyncio.Lock()

OLLAMA_CLIENT = None
