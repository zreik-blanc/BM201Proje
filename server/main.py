from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict

app = FastAPI()

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
    return {"message": "LLM Websocket is running!"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Logic: If LLM sends a command, forward it to Unity
            if client_id == "llm":
                if(manager.active_connections.get("unity")):
                    print(f"LLM sent command: {data}")
                    await manager.send_message(data, "unity")
                else:
                    await manager.send_message(f"Unity is not connected. Cannot send command: {data}", "llm")
            
            # Logic: If Unity sends data (e.g. confirmation), send to LLM to get confirmation
            elif client_id == "unity":
                if(manager.active_connections.get("llm")):
                    print(f"Unity sent message: {data}")
                    await manager.send_message(f"Unity says: {data}", "llm")
                else:
                    await manager.send_message(f"LLM is not connected. Cannot forward message: {data}", "unity")
            
            else:
                await manager.send_message(f"{client_id} said: {data}", client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        print(f"Client #{client_id} disconnected")
