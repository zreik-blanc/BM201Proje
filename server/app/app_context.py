import asyncio
from faster_whisper import WhisperModel
from typing import Optional

TTS_MODEL: None

WHISPER_MODEL: Optional[WhisperModel] = None

MODEL_LOCK = asyncio.Lock()

OLLAMA_CLIENT = None
