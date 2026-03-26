import logging
import os
from datetime import datetime, timezone

import redis
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.core.security import decrypt_api_key
from app.models.job import RecapJob
from app.models.user import User
from app.services.storage import storage
from app.services.user_service import user_requires_api_key
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

# Celery tasks use sync DB engine (not async)
_sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
sync_engine = create_engine(_sync_db_url)
SyncSession = sessionmaker(bind=sync_engine)

_redis_client = redis.from_url(settings.REDIS_URL)


def _update_job_sync(job_id: str, **kwargs):
    """Update job in DB synchronously (for use in Celery tasks)."""
    with SyncSession() as session:
        job = session.execute(
            select(RecapJob).where(RecapJob.id == job_id)
        ).scalar_one_or_none()
        if not job:
            return
        for key, value in kwargs.items():
            setattr(job, key, value)
        session.commit()


def _publish_progress(job_id: str, **kwargs):
    """Publish progress to Redis pub/sub for WebSocket consumers."""
    import json
    channel = f"job:{job_id}:progress"
    message = json.dumps({
        "type": "progress",
        **kwargs,
    })
    _redis_client.publish(channel, message)


def _combined_update(job_id: str, **kwargs):
    """Update DB and publish to Redis."""
    _update_job_sync(job_id, **{k: v for k, v in kwargs.items()
                                 if k in {"status", "current_step", "current_step_name",
                                          "progress_pct", "error_message", "output_video_key",
                                          "intermediate_keys", "completed_at", "expires_at",
                                          "started_at"}})
    _publish_progress(job_id, **kwargs)


def _resolve_openai_key(user_id: str) -> str | None:
    """Return the decrypted user key if required, else None (use system key)."""
    with SyncSession() as session:
        user = session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        if not user:
            return None
        if user_requires_api_key(user.email) and user.encrypted_openai_key:
            return decrypt_api_key(user.encrypted_openai_key)
    return None


@celery_app.task(bind=True, name="app.workers.tasks.process_recap_job")
def process_recap_job(self, job_id: str):
    """Main task: runs the 7-step recap pipeline."""
    logger.info(f"Starting recap pipeline for job {job_id}")

    # Mark job as started
    _update_job_sync(job_id, status="processing", started_at=datetime.now(timezone.utc))

    # Load job config and resolve user's OpenAI key
    user_openai_key = None
    with SyncSession() as session:
        job = session.execute(
            select(RecapJob).where(RecapJob.id == job_id)
        ).scalar_one_or_none()
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        job_config = job.config
        input_video_key = job.input_video_key
        user_openai_key = _resolve_openai_key(job.user_id)

    # Store celery task ID
    _update_job_sync(job_id, celery_task_id=self.request.id)

    # Inject user's OpenAI API key if present (concurrency=1, no race)
    original_key = os.environ.get("OPENAI_API_KEY")
    if user_openai_key:
        os.environ["OPENAI_API_KEY"] = user_openai_key
        logger.info(f"Using user-provided OpenAI key for job {job_id}")

    from app.workers.pipeline import RecapPipeline

    def publish_fn(**kwargs):
        _combined_update(job_id, **kwargs)

    pipeline = RecapPipeline(
        job_id=job_id,
        job_config=job_config,
        input_video_key=input_video_key,
        update_job_fn=lambda jid, **kw: _update_job_sync(jid, **{
            k: v for k, v in kw.items()
            if k in {"status", "current_step", "current_step_name", "progress_pct",
                      "error_message", "output_video_key", "intermediate_keys",
                      "completed_at", "expires_at", "started_at"}
        }),
        publish_progress_fn=publish_fn,
    )

    try:
        result = pipeline.run()
        # Publish completion event
        import json
        _redis_client.publish(
            f"job:{job_id}:progress",
            json.dumps({"type": "completed", "step": 7, "progress_pct": 100.0,
                        "output_video_key": result["output_key"]}),
        )
        logger.info(f"Pipeline completed for job {job_id}")
    except Exception as e:
        logger.exception(f"Pipeline failed for job {job_id}: {e}")
        import json
        _redis_client.publish(
            f"job:{job_id}:progress",
            json.dumps({"type": "failed", "error": str(e)}),
        )
    finally:
        if user_openai_key:
            if original_key is not None:
                os.environ["OPENAI_API_KEY"] = original_key
            else:
                os.environ.pop("OPENAI_API_KEY", None)


@celery_app.task(name="app.workers.tasks.cleanup_expired_files")
def cleanup_expired_files():
    """Periodic task: delete expired job files from S3."""
    logger.info("Running expired file cleanup")
    now = datetime.now(timezone.utc)

    with SyncSession() as session:
        expired_jobs = session.execute(
            select(RecapJob).where(
                RecapJob.expires_at < now,
                RecapJob.status == "completed",
            )
        ).scalars().all()

        for job in expired_jobs:
            keys_to_delete = []
            if job.output_video_key:
                keys_to_delete.append(job.output_video_key)
            if job.intermediate_keys:
                keys_to_delete.extend(job.intermediate_keys.values())
            if job.input_video_key:
                keys_to_delete.append(job.input_video_key)

            if keys_to_delete:
                storage.delete_files(keys_to_delete)

            job.status = "expired"
            job.output_video_key = None
            job.intermediate_keys = None

        session.commit()

    logger.info(f"Cleaned up {len(expired_jobs)} expired jobs")
