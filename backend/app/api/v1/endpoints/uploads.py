import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.api.v1.deps import get_current_user_or_api_key
from app.config import settings
from app.models.user import User
from app.schemas.upload import UploadResponse
from app.services.storage import storage

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


@router.post("/video", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile,
    current_user: User = Depends(get_current_user_or_api_key),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file to check size
    content = await file.read()
    size = len(content)
    if size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Max 2GB.")

    upload_id = str(uuid.uuid4())
    s3_key = f"uploads/{current_user.id}/{upload_id}/{file.filename}"

    import io
    storage.upload_file(s3_key, io.BytesIO(content))

    return UploadResponse(
        upload_id=upload_id,
        s3_key=s3_key,
        filename=file.filename,
        size=size,
    )


@router.delete("/{s3_key:path}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(
    s3_key: str,
    current_user: User = Depends(get_current_user_or_api_key),
):
    if not s3_key.startswith(f"uploads/{current_user.id}/"):
        raise HTTPException(status_code=403, detail="Not your upload")
    if not storage.file_exists(s3_key):
        raise HTTPException(status_code=404, detail="File not found")
    storage.delete_file(s3_key)
