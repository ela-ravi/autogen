import boto3
import redis.asyncio as redis
from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    services = {"database": False, "redis": False, "storage": False}

    # Check database
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        services["database"] = True
    except Exception:
        pass

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
        services["redis"] = True
    except Exception:
        pass

    # Check S3/MinIO
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        s3.head_bucket(Bucket=settings.S3_BUCKET)
        services["storage"] = True
    except Exception:
        pass

    all_healthy = all(services.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": services,
    }
