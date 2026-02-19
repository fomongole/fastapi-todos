def test_read_todos_unauthorized(client):
    response = client.get("/todos/")
    
    assert response.status_code == 401
    assert response.json() == {
        "error": "Client Error", 
        "message": "Not authenticated"
    }

def test_register_and_login(client):
    user_data = {"email": "testuser@example.com", "password": "securepassword"}
    reg_res = client.post("/users/register", json=user_data)
    assert reg_res.status_code == 201

    login_data = {"username": "testuser@example.com", "password": "securepassword"}
    login_res = client.post("/users/login", data=login_data)
    assert login_res.status_code == 200
    
    token = login_res.json()["access_token"]
    assert token is not None

def test_create_todo_authenticated(client):
    # Create a user and get a token
    user_data = {"email": "todo-owner@example.com", "password": "password123"}
    client.post("/users/register", json=user_data)
    
    login_res = client.post("/users/login", data={"username": "todo-owner@example.com", "password": "password123"})
    token = login_res.json()["access_token"]

    # Create a Todo using the Bearer Token
    headers = {"Authorization": f"Bearer {token}"}
    todo_payload = {
        "title": "Build an Enterprise API",
        "description": "Used FastAPI, Postgres, and Docker",
        "completed": False
    }
    
    response = client.post("/todos/", json=todo_payload, headers=headers)

    # The Assertions: Verify it worked
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Build an Enterprise API"
    assert "id" in data
    
    # Verification: Check if we can now see it in the list
    list_response = client.get("/todos/", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["title"] == "Build an Enterprise API"
    
    
def test_read_todos_filtering_and_search(client):
    # Register and Login a fresh user for this test
    client.post("/users/register", json={"email": "filteruser@example.com", "password": "password123"})
    login_res = client.post("/users/login", data={"username": "filteruser@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Seed the database with 3 distinct Todos
    todos_to_create = [
        {"title": "Buy groceries", "description": "Milk and eggs", "completed": False, "priority": 3},
        {"title": "Learn FastAPI", "description": "Study filtering", "completed": True, "priority": 1},
        {"title": "Fix Docker bug", "description": "Enterprise API", "completed": False, "priority": 1}
    ]
    for t in todos_to_create:
        client.post("/todos/", json=t, headers=headers)

    # Test Filter: completed=True
    res_completed = client.get("/todos/?completed=true", headers=headers)
    assert res_completed.status_code == 200
    assert len(res_completed.json()) == 1
    assert res_completed.json()[0]["title"] == "Learn FastAPI"

    # Test Filter: priority=1
    res_priority = client.get("/todos/?priority=1", headers=headers)
    assert len(res_priority.json()) == 2  # Should grab both "Learn FastAPI" and "Fix Docker bug"

    # Test Search: search=enterprise (Case-Insensitive check)
    res_search = client.get("/todos/?search=enterprise", headers=headers)
    assert len(res_search.json()) == 1
    assert res_search.json()[0]["title"] == "Fix Docker bug"

    # Test Combined Filters: completed=False AND priority=1
    res_combined = client.get("/todos/?completed=false&priority=1", headers=headers)
    assert len(res_combined.json()) == 1
    assert res_combined.json()[0]["title"] == "Fix Docker bug"