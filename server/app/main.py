from fastapi import FastAPI
from .config import check_keys
from .routers import system, websocket

# 1. Validate Environment on startup
check_keys()

# 2. Create App
app = FastAPI(
    docs_url=None, 
    redoc_url=None, 
    openapi_url=None
)

# 3. Include Routers
app.include_router(system.router)
app.include_router(websocket.router)