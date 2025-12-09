from fastapi import FastAPI
from faster_whisper import WhisperModel

from . import app_context
from .config import check_keys, WHISPER_MODEL_SIZE, DEVICE
from .routers import system, websocket, assistant

# Initializing the AI models
print(
    f"--- Global Load: Loading Faster-Whisper ({WHISPER_MODEL_SIZE}) onto {DEVICE}..."
)
try:
    compute_type = "float16" if DEVICE == "cuda" else "int8"
    app_context.WHISPER_MODEL = WhisperModel(
        WHISPER_MODEL_SIZE, device=DEVICE, compute_type=compute_type
    )
    print(
        f"--- Global Load: Faster-Whisper (compute_type: {compute_type}) loaded successfully."
    )
except Exception as e:
    print(f"Faster-Whisper failed to load: {e}")
    exit(1)


# 1. Validate Environment on startup
check_keys()

# 2. Create App
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# 3. Include Routers
app.include_router(system.router)
app.include_router(websocket.router)

app.include_router(assistant.router)
