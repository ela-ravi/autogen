import json

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user_or_api_key, get_db
from app.core.security import decode_token
from app.models.user import User
from app.services import user_service
from app.services.notification import manager, subscribe_to_job

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/jobs/{job_id}")
async def job_progress_ws(
    websocket: WebSocket,
    job_id: str,
    token: str = Query(...),
):
    # Authenticate via token query param
    try:
        payload = decode_token(token)
        user_id = payload["sub"]
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(job_id, websocket)
    try:
        async for data in subscribe_to_job(job_id):
            await websocket.send_text(json.dumps(data))
            if data.get("type") in ("completed", "failed"):
                break
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(job_id, websocket)


@router.get("/jobs/{job_id}/events")
async def job_progress_sse(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
):
    """SSE fallback for real-time job progress."""

    async def event_stream():
        async for data in subscribe_to_job(job_id):
            yield f"data: {json.dumps(data)}\n\n"
            if data.get("type") in ("completed", "failed"):
                break

    return StreamingResponse(event_stream(), media_type="text/event-stream")
