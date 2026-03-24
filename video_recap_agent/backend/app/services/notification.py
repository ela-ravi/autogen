import asyncio
import json
import logging
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import WebSocket

from app.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections per job."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)

    def disconnect(self, job_id: str, websocket: WebSocket):
        if job_id in self.active_connections:
            self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def broadcast(self, job_id: str, message: dict):
        if job_id not in self.active_connections:
            return
        data = json.dumps(message)
        for ws in self.active_connections[job_id]:
            try:
                await ws.send_text(data)
            except Exception:
                pass


manager = ConnectionManager()


async def subscribe_to_job(job_id: str) -> AsyncGenerator[dict, None]:
    """Subscribe to Redis pub/sub channel for a job and yield messages."""
    r = aioredis.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    channel = f"job:{job_id}:progress"

    try:
        await pubsub.subscribe(channel)
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                yield data
                if data.get("type") in ("completed", "failed"):
                    break
            await asyncio.sleep(0.1)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        await r.aclose()
