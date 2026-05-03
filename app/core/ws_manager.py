import json
from collections import defaultdict

from fastapi import WebSocket


class VoteConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, board_id: str):
        await websocket.accept()
        self.active_connections[board_id].append(websocket)


    def disconnect(self, websocket: WebSocket, board_id: str):
        if websocket in self.active_connections[board_id]:
            self.active_connections[board_id].remove(websocket)

    async def broadcast(self, board_id: str, message: dict):
        dead = []
        for connection in self.active_connections[board_id]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead.append(connection) 
        
        for connection in dead:
            self.active_connections[board_id].remove(connection) 

manager = VoteConnectionManager()
