import json
import os
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, status
from typing import Dict

app = FastAPI(
    docs_url = None,
    redoc_url = None,
    openapi_url = None
)

CONTROLLER_ID = "LLM"
LLM_SECRET_KEY = os.environ.get("LLM_SECRET_KEY")
UNITY_CLIENT_KEY = os.environ.get("UNITY_CLIENT_KEY")

if not LLM_SECRET_KEY or not UNITY_CLIENT_KEY:
    print("CRITICAL ERROR: Security keys are missing from environment variables.")
    print("Please set LLM_SECRET_KEY and UNITY_CLIENT_KEY.")
    sys.exit(1)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "LLM Websocket is running!", "version": "1.0.0"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    client_id: str, 
    x_auth_token: str | None = Header(default=None)):

    # Authentication
    is_authorized = False

    if client_id == CONTROLLER_ID:
        if x_auth_token == LLM_SECRET_KEY:
            is_authorized = True
    else:
        if x_auth_token == UNITY_CLIENT_KEY:
            is_authorized = True

    if not is_authorized:
        print(f"Unauthorized connection attempt: {client_id} with token: {x_auth_token}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_text()
            
            if client_id == CONTROLLER_ID:
                try:
                    message_data = json.loads(data)
                    target = message_data.get("target")
                    command = message_data.get("message")
                    
                    if target and command:
                        if manager.active_connections.get(target):
                            print(f"{CONTROLLER_ID} sent command to {target}: {command}")
                            await manager.send_message(command, target)
                        else:
                            await manager.send_message(f"Target '{target}' is not connected. Cannot send command.", CONTROLLER_ID)
                    else:
                        await manager.send_message("Invalid JSON format. Expected {'target': '...', 'message': '...'}", CONTROLLER_ID)
                except json.JSONDecodeError:
                     await manager.send_message("Invalid message format. Please send JSON.", CONTROLLER_ID)

            # Logic: If a device/client sends data, forward it to the LLM
            else:
                if manager.active_connections.get(CONTROLLER_ID):
                    print(f"{client_id} sent message: {data}")
                    response = json.dumps({"sender": client_id, "message": data})
                    await manager.send_message(response, CONTROLLER_ID)
                else:
                    print(f"{CONTROLLER_ID} not connected, dropping message from {client_id}: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        print(f"Client #{client_id} disconnected")
