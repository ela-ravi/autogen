import pytest


@pytest.mark.asyncio
async def test_signup(client):
    response = await client.post(
        "/api/v1/auth/signup",
        json={"email": "new@test.com", "password": "Test123!", "full_name": "New User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(client):
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "dup@test.com", "password": "Test123!", "full_name": "User"},
    )
    response = await client.post(
        "/api/v1/auth/signup",
        json={"email": "dup@test.com", "password": "Test123!", "full_name": "User 2"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client):
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "login@test.com", "password": "Test123!", "full_name": "User"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "Test123!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nope@test.com", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me(authenticated_client):
    response = await authenticated_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@test.com"
    assert data["full_name"] == "Test User"


@pytest.mark.asyncio
async def test_refresh(client):
    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "refresh@test.com", "password": "Test123!", "full_name": "User"},
    )
    refresh_token = signup_resp.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
