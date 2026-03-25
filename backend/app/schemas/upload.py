from pydantic import BaseModel


class UploadResponse(BaseModel):
    upload_id: str
    s3_key: str
    filename: str
    size: int
