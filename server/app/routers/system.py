from fastapi import APIRouter
from ..connection_manager import manager

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "LLM Websocket is running!", "version": "1.0.1"}

@router.get("/active_clients")
async def active_clients():
    return {"active_clients": list(manager.active_connections.keys())}