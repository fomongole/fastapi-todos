# FastAPI Todos 🚀

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://example.com)
[![Python](https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-enabled-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Redis](https://img.shields.io/badge/redis-required-red?logo=redis&logoColor=white)](https://redis.io/)
[![Firebase](https://img.shields.io/badge/firebase-required-yellow?logo=firebase&logoColor=black)](https://firebase.google.com/)

A high-performance, production-grade Todo API backend.  
This project showcases **Clean Architecture**, **Distributed Caching**, and **Real-time Notifications** to support modern mobile and web applications.

---

## ✨ New & Advanced Features

- 📶 **API Versioning**  
  Standardized `/api/v1/` prefix for future-proof mobile client support.

- ⚡ **Distributed Caching**  
  Integration with Redis using `fastapi-cache` to slash database load and response times.

- 🔔 **Real-time Reminders**  
  Firebase Cloud Messaging (FCM) integration for push notifications.

- 🤖 **Background Workers**  
  Asynchronous reminder service that checks for due tasks without blocking the main API.

- 📂 **Hierarchical Organization**  
  Support for Categories (Labels/Folders) with custom hex colors and Sub-tasks (Checklists).

- 🌍 **Global Timezone Sync**  
  Strict UTC internal handling to ensure reminders are accurate across all world timezones.

- 🛡️ **Enhanced Security**  
  JWT-based session management with a Redis-backed token denylist for secure logouts.

---

## 🛠️ Updated Tech Stack

- **Framework:** FastAPI  
- **Cache & Denylist:** Redis  
- **Notifications:** Firebase Admin SDK  
- **Background Tasks:** Python asyncio Event Loop (or Celery/RQ for heavier workloads)  
- **ORM & Migrations:** SQLAlchemy 2.0 & Alembic  
- **Database:** PostgreSQL  

---

## 🚀 Getting Started

### 📋 Prerequisites

- Docker & Docker Compose  
- Firebase Service Account Key  
  (Place as `serviceAccountKey.json` in project root)

---

## ⚙️ Environment Configuration

Update your `.env` file with the following:

```env
PROJECT_NAME="Fred-Todos-Pro"
DATABASE_URL="postgresql://postgres:password@db:5432/todos_db"
REDIS_URL="redis://redis:6379/0"
SECRET_KEY="your-complex-secret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
FCM_SERVICE_ACCOUNT_PATH="./serviceAccountKey.json"
```

---

## 🐳 Installation

```bash
# Build and bring up App, Postgres, and Redis
docker-compose up --build -d

# Run migrations to build the new Category and Sub-task tables
docker-compose exec api alembic upgrade head
```

---

## 📁 Modular Project Structure

```plaintext
fastapi-todos/
├── app/
│   ├── core/           
│   │   ├── cache.py          # Redis custom key builders and cache helpers
│   │   ├── worker.py         # Background reminder ticker
│   │   └── notifications.py  # FCM Logic
│   ├── todos/          
│   │   ├── models.py         # Multi-table schema (Todo, Category, SubTask)
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── router.py
│   └── users/          
│       ├── dependencies.py   # Auth & Redis denylist check
│       └── router.py
├── tests/              
│   ├── test_users.py         # Specialized Auth tests
│   └── test_todos.py         # Domain logic & Pagination tests
├── docker-compose.yml
├── Dockerfile
├── alembic/
└── serviceAccountKey.json    # Firebase credentials (Git-ignored!)
```

---

## 🧪 Testing the New Architecture

```bash
# Run the test suite inside the running api container
docker-compose exec api pytest -q
```

---

## 📖 API Documentation

Access the upgraded v1 documentation locally:

- **Swagger UI:** http://localhost:8000/docs  
- **Prefix:** All endpoints are located at `/api/v1/`

---

## 🏗️ Architecture Diagram

Below are two formats — a Mermaid diagram (works where Mermaid is supported) and an ASCII fallback.

### Mermaid (recommended view on GitHub with Mermaid enabled)

```mermaid
flowchart LR
  Client[Client (Web / Mobile)] -->|HTTPS| API[FastAPI (/api/v1)]
  API --> DB[(PostgreSQL)]
  API --> Redis[(Redis Cache & Denylist)]
  API --> FCM[Firebase Cloud Messaging]
  API --> Worker[Background Worker (async)]
  Worker --> DB
  Worker --> FCM
  subgraph Storage
    DB
    Redis
  end
```

### ASCII Fallback

```
  +------------------+         +-------------+       +-----------+
  | Client (Web/Mobile) | ---> | FastAPI API | --->  | PostgreSQL |
  +------------------+         +------^------+       +-----------+
                                      |
                            +---------+----------+
                            | Redis (cache/denylist) |
                            +-----------------------+
                                      |
                                +-----v------+
                                |  Worker    |
                                | (background)|
                                +-----+------+
                                      |
                                    FCM (push)
```

---

## ⚙️ Cache & Denylist Notes

- The API uses `fastapi-cache` with the Redis backend. **Do not** set `decode_responses=True` when using binary cache payloads — use raw bytes.
- In production, **never** allow cache errors to surface to clients. Use fail-safe cache reads/writes with try/except and fall back to DB on errors.

---

## 🧾 Category Deletion Policy

Recommended: mark `ON DELETE SET NULL` for the `categories.id` FK so deleting a category preserves todos (they become uncategorized). This is preferred UX for productivity apps.

```sql
ALTER TABLE todos
  DROP CONSTRAINT IF EXISTS todos_category_id_fkey,
  ADD CONSTRAINT todos_category_id_fkey
  FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL;
```

---

## ✅ Pydantic Best Practices

Avoid mutable defaults:

```py
from pydantic import BaseModel, Field

sub_tasks: List[SubTaskCreate] = Field(default_factory=list)
```

---

## 🔐 Security Notes

- Use a strong `SECRET_KEY` and rotate it as needed.
- Use HTTPS in production and restrict CORS origins.
- Use Redis denylist for refresh tokens so logged-out tokens cannot be reused.

---

## License

MIT — see [LICENSE](LICENSE) for details.
