from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # project_id -> [WebSocket]

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        self.active_connections.setdefault(project_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str):
        self.active_connections[project_id].remove(websocket)
        if not self.active_connections[project_id]:
            del self.active_connections[project_id]

    async def broadcast(self, project_id: str, message: dict):
        for connection in self.active_connections.get(project_id, []):
            await connection.send_json(message)

manager = ConnectionManager()
