import pytest

# This marker tells pytest to treat all functions in this file as async coroutines
pytestmark = pytest.mark.anyio

async def test_register_and_login(client):
    user_data = {"email": "testuser@example.com", "password": "securepassword"}
    reg_res = await client.post("/api/v1/users/register", json=user_data) 
    assert reg_res.status_code == 201

    login_data = {"username": "testuser@example.com", "password": "securepassword"}
    login_res = await client.post("/api/v1/users/login", data=login_data)
    assert login_res.status_code == 200
    
    data = login_res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

async def test_token_refresh_flow(client):
    user_data = {"email": "refreshuser@example.com", "password": "securepassword"}
    await client.post("/api/v1/users/register", json=user_data)
    
    login_res = await client.post("/api/v1/users/login", data={"username": "refreshuser@example.com", "password": "securepassword"})
    refresh_token = login_res.json()["refresh_token"]
    old_access_token = login_res.json()["access_token"]
    
    # Hit the refresh endpoint
    refresh_res = await client.post("/api/v1/users/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["access_token"] != old_access_token

async def test_logout_endpoint(client):
    user_data = {"email": "logoutuser@example.com", "password": "securepassword"}
    await client.post("/api/v1/users/register", json=user_data)
    
    login_res = await client.post("/api/v1/users/login", data={"username": "logoutuser@example.com", "password": "securepassword"})
    access_token = login_res.json()["access_token"]
    refresh_token = login_res.json()["refresh_token"]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    logout_res = await client.post("/api/v1/users/logout", json={"refresh_token": refresh_token}, headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Successfully logged out!"