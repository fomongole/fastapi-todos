# FastAPI Todos 🚀

A professional, high-performance, and secure Todo application backend built with **FastAPI**, **PostgreSQL**, and **Docker**. This project follows **Clean Architecture** principles, separating concerns into Routers, Services, and Repositories.

---

## ✨ Features

- **⚡ FastAPI**: High-performance Python framework for building APIs.
- **🐘 PostgreSQL**: Production-grade relational database.
- **🐳 Dockerized**: Fully containerized stack (App + Database) using Docker Compose.
- **🔒 JWT Authentication**: Secure user registration and login using OAuth2 with JSON Web Tokens.
- **🛡️ Data Isolation**: Multi-tenant architecture ensuring users can only access their own data.
- **🏗️ Database Migrations**: Version-controlled schema changes using **Alembic**.
- **🧪 Automated Testing**: Comprehensive test suite using **Pytest** and **HTTPX**.
- **🤖 CI/CD Ready**: Pre-configured GitHub Actions workflow.

---

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database:** [PostgreSQL](https://www.postgresql.org/)
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Security:** [Passlib (Bcrypt)](https://passlib.readthedocs.io/), [PyJWT](https://pyjwt.readthedocs.io/)
- **Validation:** [Pydantic v2](https://docs.pydantic.dev/)

---

## 🚀 Getting Started

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine.
- [Git](https://git-scm.com/) (optional).

### Installation & Setup

1. **Clone the repository:**
   ```bash
        git clone [https://github.com/fomongole/fastapi-todos.git](https://github.com/fomongole/fastapi-todos.git)
        cd fastapi-todos
    ```

## ⚙️ Configure Environment Variables

Create a `.env` file in the root directory:

```env
PROJECT_NAME="Fred-Todos"
PROJECT_VERSION="1.0.0"
DATABASE_URL="postgresql://postgres:supersecretpassword@db:5432/todos_db"
SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🚀 Spin Up the Stack

```bash
docker-compose up --build -d
```

---

## 🗄️ Run Database Migrations

```bash
docker exec -it todos_fastapi_app alembic upgrade head
```

---

## 📖 API Documentation

Once the app is running, access the interactive documentation at:

- **Swagger UI:** http://localhost:8000/docs  
- **ReDoc:** http://localhost:8000/redoc  

---

## 🧪 Running Tests

To run the automated test suite locally:

```bash
# Ensure you are in your virtual environment
pip install pytest httpx
pytest
```

---

## 📁 Project Structure

```plaintext
fastapi-todos/
├── app/
│   ├── core/           # Configuration and Security utilities
│   ├── database/       # Database connection and Session logic
│   ├── todos/          # Todo Domain (Models, Schemas, Repo, Service, Router)
│   ├── users/          # User Domain (Auth logic, Models, Schemas, etc.)
│   └── main.py         # Entry point
├── alembic/            # Database migrations
├── tests/              # Pytest suite
├── .github/            # GitHub Actions CI workflows
├── Dockerfile          # App container recipe
├── docker-compose.yml  # Orchestration file
└── requirements.txt    # Python dependencies
```

---

## 🔐 Security Best Practices

- **Password Hashing:** Never stored in plain text. Uses bcrypt.  
- **JWT Tokens:** Short-lived access tokens for session management.  
- **Dependency Injection:** Used for database sessions and user authentication.  
- **Validation:** Strict Pydantic models to prevent malformed data entry.  

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
