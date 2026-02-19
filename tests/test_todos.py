import pytest

# This marker tells pytest to treat all functions in this file as async coroutines
pytestmark = pytest.mark.anyio

async def test_read_todos_unauthorized(client):
    response = await client.get("/todos/")
    
    assert response.status_code == 401
    assert response.json() == {
        "error": "Client Error", 
        "message": "Not authenticated"
    }

async def test_register_and_login(client):
    user_data = {"email": "testuser@example.com", "password": "securepassword"}
    reg_res = await client.post("/users/register", json=user_data) 
    assert reg_res.status_code == 201

    login_data = {"username": "testuser@example.com", "password": "securepassword"}
    login_res = await client.post("/users/login", data=login_data)
    assert login_res.status_code == 200
    
    data = login_res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

async def test_token_refresh_flow(client):
    user_data = {"email": "refreshuser@example.com", "password": "securepassword"}
    await client.post("/users/register", json=user_data)
    
    login_res = await client.post("/users/login", data={"username": "refreshuser@example.com", "password": "securepassword"})
    refresh_token = login_res.json()["refresh_token"]
    old_access_token = login_res.json()["access_token"]
    
    # Hit the refresh endpoint
    refresh_res = await client.post("/users/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["access_token"] != old_access_token

async def test_logout_endpoint(client):
    user_data = {"email": "logoutuser@example.com", "password": "securepassword"}
    await client.post("/users/register", json=user_data)
    
    login_res = await client.post("/users/login", data={"username": "logoutuser@example.com", "password": "securepassword"})
    access_token = login_res.json()["access_token"]
    refresh_token = login_res.json()["refresh_token"]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    logout_res = await client.post("/users/logout", json={"refresh_token": refresh_token}, headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Successfully logged out!"

async def test_create_todo_authenticated(client):
    user_data = {"email": "todo-owner@example.com", "password": "password123"}
    await client.post("/users/register", json=user_data)
    login_res = await client.post("/users/login", data={"username": "todo-owner@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    todo_payload = {
        "title": "Build an Enterprise API",
        "description": "Used FastAPI, Postgres, and Docker",
        "completed": False
    }
    
    response = await client.post("/todos/", json=todo_payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Build an Enterprise API"
    
    list_response = await client.get("/todos/", headers=headers)
    assert list_response.status_code == 200
    res_data = list_response.json()
    
    # Asserting paginated structure
    assert "items" in res_data
    assert res_data["total"] == 1
    assert res_data["items"][0]["title"] == "Build an Enterprise API"
    
async def test_read_todos_filtering_and_search(client):
    await client.post("/users/register", json={"email": "filteruser@example.com", "password": "password123"})
    login_res = await client.post("/users/login", data={"username": "filteruser@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    todos_to_create = [
        {"title": "Buy groceries", "description": "Milk and eggs", "completed": False, "priority": 3},
        {"title": "Learn FastAPI", "description": "Study filtering", "completed": True, "priority": 1},
        {"title": "Fix Docker bug", "description": "Enterprise API", "completed": False, "priority": 1}
    ]
    for t in todos_to_create:
        await client.post("/todos/", json=t, headers=headers)
    
    # Test Filter: completed=True (check inside .json()["items"])
    res_completed = await client.get("/todos/?completed=true", headers=headers)
    assert len(res_completed.json()["items"]) == 1
    assert res_completed.json()["items"][0]["title"] == "Learn FastAPI"

    # Test Search: search=enterprise
    res_search = await client.get("/todos/?search=enterprise", headers=headers)
    assert len(res_search.json()["items"]) == 1
    assert res_search.json()["items"][0]["title"] == "Fix Docker bug"