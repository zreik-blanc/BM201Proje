from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root() -> dict:
    return {"message": "LLM Websocket is running!", "version": "1.0.3"}
