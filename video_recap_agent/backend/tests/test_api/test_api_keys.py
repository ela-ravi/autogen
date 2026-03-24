import pytest


@pytest.mark.asyncio
async def test_create_api_key(authenticated_client):
    response = await authenticated_client.post(
        "/api/v1/api-keys",
        json={"name": "Test Key"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "key" in data
    assert data["name"] == "Test Key"
    assert data["key_prefix"].startswith("vra_")


@pytest.mark.asyncio
async def test_list_api_keys(authenticated_client):
    # Create a key first
    await authenticated_client.post(
        "/api/v1/api-keys",
        json={"name": "My Key"},
    )
    response = await authenticated_client.get("/api/v1/api-keys")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    # Full key should NOT be in list response
    assert "key" not in data[0]


@pytest.mark.asyncio
async def test_revoke_api_key(authenticated_client):
    create_resp = await authenticated_client.post(
        "/api/v1/api-keys",
        json={"name": "Revokable Key"},
    )
    key_id = create_resp.json()["id"]

    response = await authenticated_client.delete(f"/api/v1/api-keys/{key_id}")
    assert response.status_code == 204
