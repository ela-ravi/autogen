from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user_or_api_key, get_db
from app.models.user import User
from app.schemas.job import CreateJobRequest, DownloadResponse, JobListResponse, JobResponse
from app.services import job_service
from app.services.storage import storage

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: CreateJobRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
):
    # Check quota before creating job
    from app.core.permissions import check_quota
    await check_quota(db, current_user.id, current_user.tier)

    # Verify the upload exists in S3
    if not storage.file_exists(body.s3_key):
        raise HTTPException(status_code=400, detail="Upload not found")

    job = await job_service.create_job(
        db,
        user_id=current_user.id,
        s3_key=body.s3_key,
        config=body.config,
        original_filename=body.original_filename,
        file_size_bytes=body.file_size_bytes,
    )

    # Record usage
    from app.services.billing_service import record_usage
    await record_usage(db, current_user.id, job.id)

    # Dispatch to Celery
    from app.workers.tasks import process_recap_job
    process_recap_job.delay(job.id)

    return job


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
):
    jobs, total = await job_service.list_jobs(
        db, current_user.id, page=page, per_page=per_page, status_filter=status_filter
    )
    return JobListResponse(items=jobs, total=total, page=page, per_page=per_page)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
):
    job = await job_service.get_job(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/download", response_model=DownloadResponse)
async def download_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
):
    job = await job_service.get_job(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed" or not job.output_video_key:
        raise HTTPException(status_code=400, detail="Job not ready for download")

    url = storage.generate_presigned_url(job.output_video_key, expires_in=3600)
    return DownloadResponse(download_url=url)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_or_api_key),
):
    deleted = await job_service.delete_job(db, job_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
