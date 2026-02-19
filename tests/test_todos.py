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