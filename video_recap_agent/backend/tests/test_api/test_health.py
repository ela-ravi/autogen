import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_health_endpoint(client):
    # Mock external services since they won't be available in tests
    with patch("app.api.v1.endpoints.health.engine") as mock_engine, \
         patch("app.api.v1.endpoints.health.redis") as mock_redis, \
         patch("app.api.v1.endpoints.health.boto3") as mock_boto3:

        # Mock DB connection
        mock_conn = AsyncMock()
        mock_engine.connect = AsyncMock(return_value=mock_conn)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock()
        mock_conn.execute = AsyncMock()

        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
