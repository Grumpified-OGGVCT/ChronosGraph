"""ChronosGraph WebSocket Connection Manager."""

from __future__ import annotations
import json
import logging
from typing import Any
from fastapi import WebSocket

logger = logging.getLogger("chronosgraph.ws")


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_json(self, websocket: WebSocket, data: dict[str, Any]) -> None:
        await websocket.send_text(json.dumps(data))

    async def broadcast(self, data: dict[str, Any]) -> None:
        message = json.dumps(data)
        disconnected = []
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except Exception:
                disconnected.append(conn)
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_status(self, state: str) -> None:
        await self.broadcast({"type": "status", "state": state})

    async def broadcast_progress(self, video: str, chunk: int, total: int) -> None:
        await self.broadcast({"type": "progress", "video": video, "chunk": chunk, "total": total})

    async def broadcast_toast(self, level: str, message: str) -> None:
        await self.broadcast({"type": "toast", "level": level, "message": message})

    async def broadcast_queue_update(self, queued: int) -> None:
        await self.broadcast({"type": "queue_update", "queued": queued})

    async def broadcast_new_node(self, node: dict[str, Any]) -> None:
        await self.broadcast({"type": "new_node", "node": node})

    async def broadcast_new_edge(self, edge: dict[str, Any]) -> None:
        await self.broadcast({"type": "new_edge", "edge": edge})


ws_manager = ConnectionManager()
