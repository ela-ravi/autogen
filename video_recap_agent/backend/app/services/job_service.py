from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import RecapJob
from app.schemas.job import JobConfig


async def create_job(
    db: AsyncSession,
    user_id: str,
    s3_key: str,
    config: JobConfig,
    original_filename: str,
    file_size_bytes: int,
) -> RecapJob:
    job = RecapJob(
        user_id=user_id,
        input_video_key=s3_key,
        config=config.model_dump(),
        original_filename=original_filename,
        file_size_bytes=file_size_bytes,
        status="pending",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_job(db: AsyncSession, job_id: str, user_id: str) -> RecapJob | None:
    result = await db.execute(
        select(RecapJob).where(RecapJob.id == job_id, RecapJob.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_jobs(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    per_page: int = 20,
    status_filter: str | None = None,
) -> tuple[list[RecapJob], int]:
    query = select(RecapJob).where(RecapJob.user_id == user_id)
    count_query = select(func.count()).select_from(RecapJob).where(RecapJob.user_id == user_id)

    if status_filter:
        query = query.where(RecapJob.status == status_filter)
        count_query = count_query.where(RecapJob.status == status_filter)

    query = query.order_by(RecapJob.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    jobs = list(result.scalars().all())

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return jobs, total


async def delete_job(db: AsyncSession, job_id: str, user_id: str) -> bool:
    job = await get_job(db, job_id, user_id)
    if not job:
        return False

    # Cancel celery task if running
    if job.celery_task_id and job.status in ("pending", "processing"):
        from app.workers.celery_app import celery_app
        celery_app.control.revoke(job.celery_task_id, terminate=True)

    # Delete S3 files
    from app.services.storage import storage
    keys_to_delete = []
    if job.input_video_key:
        keys_to_delete.append(job.input_video_key)
    if job.output_video_key:
        keys_to_delete.append(job.output_video_key)
    if job.intermediate_keys:
        keys_to_delete.extend(job.intermediate_keys.values())
    if keys_to_delete:
        storage.delete_files(keys_to_delete)

    await db.delete(job)
    await db.commit()
    return True
