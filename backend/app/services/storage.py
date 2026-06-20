import logging
import mimetypes
import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)


# Custom MIME overrides for file types where Python's mimetypes guess is
# missing or unhelpful (e.g. .json on older stdlib, .mp4 vs application/mp4).
_MIME_OVERRIDES = {
    ".json": "application/json",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".txt": "text/plain",
}


def _guess_content_type(key: str) -> str:
    """Pick a sensible Content-Type from the object key's file extension.

    S3 defaults uploads to application/octet-stream, which makes browsers
    save downloads as generic "documents". Setting Content-Type at upload
    time lets presigned downloads carry the right type without per-download
    overrides.
    """
    lower_key = key.lower()
    for ext, mime in _MIME_OVERRIDES.items():
        if lower_key.endswith(ext):
            return mime
    guessed, _ = mimetypes.guess_type(key)
    return guessed or "application/octet-stream"


class StorageService:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        self.bucket = settings.S3_BUCKET

    def upload_file(self, key: str, file_obj) -> None:
        try:
            content_type = _guess_content_type(key)
            self.client.upload_fileobj(
                file_obj,
                self.bucket,
                key,
                ExtraArgs={"ContentType": content_type},
            )
            logger.info(f"✅ Uploaded S3: {key} ({content_type})")
        except Exception as e:
            logger.error(f"❌ Failed to upload S3 {key}: {str(e)}", exc_info=True)
            raise

    def upload_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)

    def download_file(self, key: str, dest_path: str) -> None:
        self.client.download_file(self.bucket, key, dest_path)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        if settings.S3_PUBLIC_ENDPOINT:
            url = url.replace(settings.S3_ENDPOINT, settings.S3_PUBLIC_ENDPOINT, 1)
        return url

    def delete_file(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def delete_files(self, keys: list[str]) -> None:
        if not keys:
            return
        objects = [{"Key": k} for k in keys]
        self.client.delete_objects(
            Bucket=self.bucket,
            Delete={"Objects": objects},
        )

    def file_exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False


storage = StorageService()
