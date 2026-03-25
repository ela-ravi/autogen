from datetime import datetime

from pydantic import BaseModel, Field


class JobConfig(BaseModel):
    target_duration: int = Field(default=30, ge=10, le=120)
    whisper_model: str = "small"
    tts_voice: str = "nova"
    tts_model: str = "tts-1"
    language: str | None = None
    translate_to: str | None = None
    pad_with_black: bool = False


class CreateJobRequest(BaseModel):
    upload_id: str
    s3_key: str
    original_filename: str
    file_size_bytes: int
    config: JobConfig = JobConfig()


class JobResponse(BaseModel):
    id: str
    user_id: str
    status: str
    current_step: int
    current_step_name: str | None
    progress_pct: float
    error_message: str | None
    original_filename: str
    file_size_bytes: int
    config: dict
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    expires_at: datetime | None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    per_page: int


class DownloadResponse(BaseModel):
    download_url: str
    expires_in: int = 3600
