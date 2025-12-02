from fastapi import APIRouter
from ..connection_manager import manager

router = APIRouter()


@router.get("/")
async def root() -> dict:
    return {"message": "LLM Websocket is running!", "version": "1.0.3"}


@router.get("/metrics")
async def metrics() -> dict:
    return {
        "active_connections": len(manager.active_connections),
        "pubsub_connections": len(manager.pubsub_connections),
    }
