import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_list_jobs_empty(authenticated_client):
    response = await authenticated_client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_jobs_unauthenticated(client):
    response = await client.get("/api/v1/jobs")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_job_not_found(authenticated_client):
    response = await authenticated_client.get("/api/v1/jobs/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_job(authenticated_client, mock_storage):
    with patch("app.api.v1.endpoints.jobs.process_recap_job") as mock_task:
        mock_task.delay = MagicMock()
        response = await authenticated_client.post(
            "/api/v1/jobs",
            json={
                "upload_id": "test-upload-id",
                "s3_key": "uploads/test/test.mp4",
                "original_filename": "test.mp4",
                "file_size_bytes": 1024000,
                "config": {"target_duration": 30},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["original_filename"] == "test.mp4"
        mock_task.delay.assert_called_once()
