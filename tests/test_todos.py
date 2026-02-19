import pytest

pytestmark = pytest.mark.anyio

async def get_auth_headers(client, email="todo-owner@example.com"):
    await client.post("/api/v1/users/register", json={"email": email, "password": "password123"})
    login_res = await client.post("/api/v1/users/login", data={"username": email, "password": "password123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

async def test_read_todos_unauthorized(client):
    response = await client.get("/api/v1/todos/")
    
    assert response.status_code == 401
    assert response.json() == {
        "error": "Client Error", 
        "message": "Not authenticated"
    }

async def test_create_category_and_todo_with_subtasks(client):
    headers = await get_auth_headers(client, "complex-user@example.com")

    # 1. Create a Category
    cat_payload = {"name": "Project Alpha", "color": "#FF0000"}
    cat_res = await client.post("/api/v1/todos/categories", json=cat_payload, headers=headers)
    assert cat_res.status_code == 201
    category_id = cat_res.json()["id"]

    # 2. Create a Todo linked to the Category with Sub-tasks
    todo_payload = {
        "title": "Launch Mobile App",
        "description": "Ensure backend is ready",
        "category_id": category_id,
        "sub_tasks": [
            {"title": "Setup Docker", "is_completed": True},
            {"title": "Run Alembic Migrations", "is_completed": False}
        ]
    }
    todo_res = await client.post("/api/v1/todos/", json=todo_payload, headers=headers)
    assert todo_res.status_code == 201
    
    data = todo_res.json()
    assert data["title"] == "Launch Mobile App"
    assert data["category"]["name"] == "Project Alpha"
    assert len(data["sub_tasks"]) == 2
    assert data["sub_tasks"][0]["title"] == "Setup Docker"

async def test_read_todos_filtering_and_search(client):
    headers = await get_auth_headers(client, "filteruser@example.com")

    todos_to_create = [
        {"title": "Buy groceries", "description": "Milk and eggs", "completed": False, "priority": 3},
        {"title": "Learn FastAPI", "description": "Study filtering", "completed": True, "priority": 1},
        {"title": "Fix Docker bug", "description": "Enterprise API", "completed": False, "priority": 1}
    ]
    for t in todos_to_create:
        await client.post("/api/v1/todos/", json=t, headers=headers)
    
    # Test Filter: completed=True
    res_completed = await client.get("/api/v1/todos/?completed=true", headers=headers)
    assert len(res_completed.json()["items"]) == 1
    assert res_completed.json()["items"][0]["title"] == "Learn FastAPI"

    # Test Search: search=enterprise
    res_search = await client.get("/api/v1/todos/?search=enterprise", headers=headers)
    assert len(res_search.json()["items"]) == 1
    assert res_search.json()["items"][0]["title"] == "Fix Docker bug"