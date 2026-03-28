from fastapi import APIRouter

from app.api.v1.endpoints import api_keys, auth, billing, health, jobs, processing, uploads, websocket

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(uploads.router)
api_router.include_router(jobs.router)
api_router.include_router(websocket.router)
api_router.include_router(api_keys.router)
api_router.include_router(billing.router)
api_router.include_router(processing.router)
