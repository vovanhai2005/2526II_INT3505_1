# Book Library API — Buoi8

A Flask-based REST API for managing a library's book catalog, with comprehensive testing coverage including unit, integration, and performance tests using Pytest and Locust.

## Overview

This project demonstrates:
- RESTful API design with Flask
- Database operations with Flask-SQLAlchemy
- Multiple pagination strategies (offset, page, cursor)
- Comprehensive test suite (unit, integration, performance)
- Load testing with Locust
- API documentation with Swagger/OpenAPI

## Project Structure

```
Buoi8/
├── app.py                      # Flask app initialization
├── config.py                   # Configuration settings
├── models.py                   # SQLAlchemy ORM models (Book)
├── routes/
│   ├── book_routes.py         # Book API endpoints (GET, POST, PUT, DELETE)
│   ├── loan_routes.py         # Loan management endpoints
│   └── user_routes.py         # User management endpoints
├── swagger.yml                 # OpenAPI 3.0 specification
├── library.db                  # SQLite database (created at runtime)
├── requirements.txt            # Python dependencies
└── tests/
    ├── conftest.py            # Pytest fixtures
    ├── README.md              # Testing guide
    ├── unit/
    │   └── test_book_unit.py              # Unit tests (5 tests)
    ├── integration/
    │   └── test_book_integration.py       # Integration tests (3 tests)
    └── performance/
        ├── locustfile.py                   # Locust load testing (RECOMMENDED)
        ├── test_book_performance.py        # Pytest performance assertions
        ├── LOCUST_GUIDE.md                 # Quick Locust reference
        └── README.md                       # (in tests/README.md)
```

## Quick Start

### 1. Setup Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the App

```bash
python app.py
```

App runs on **http://localhost:8080**

Access Swagger UI: **http://localhost:8080/apidocs**

### 3. Run Tests

```bash
# All tests (unit + integration + performance)
python -m pytest tests/ -v

# Just unit tests
python -m pytest tests/unit/ -v

# Just integration tests
python -m pytest tests/integration/ -v

# Just pytest performance tests
python -m pytest tests/performance/test_book_performance.py -v
```

### 4. Run Load Tests (Locust)

**Terminal 1: Start the app**
```bash
python app.py
```

**Terminal 2: Start Locust**
```bash
locust -f tests/performance/locustfile.py
```

Open **http://localhost:8089** and start swarming with 10 users, spawn rate 2.

---

## API Endpoints

### Books

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books` | List all books (supports filtering by category/author, pagination) |
| GET | `/api/books/<id>` | Get a single book by ID |
| POST | `/api/books` | Create a new book |
| PUT | `/api/books/<id>` | Update an existing book |
| DELETE | `/api/books/<id>` | Delete a book |

### Example Requests

**List all books:**
```bash
curl http://localhost:8080/api/books
```

**List with pagination (offset-based):**
```bash
curl http://localhost:8080/api/books?limit=5&offset=0&pagination_type=offset
```

**Filter by category:**
```bash
curl http://localhost:8080/api/books?category=Programming
```

**Create a book:**
```bash
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","author":"Robert Martin","category":"Programming","available_copies":3}'
```

**Update a book:**
```bash
curl -X PUT http://localhost:8080/api/books/1 \
  -H "Content-Type: application/json" \
  -d '{"available_copies":5}'
```

**Delete a book:**
```bash
curl -X DELETE http://localhost:8080/api/books/1
```

---

## Testing Guide

### Three Testing Approaches

| Type | Tool | Purpose | Location |
|------|------|---------|----------|
| **Unit Tests** | Pytest | Verify individual endpoints in isolation | `tests/unit/` |
| **Integration Tests** | Pytest | Verify multi-step workflows and state changes | `tests/integration/` |
| **Performance Tests** | Pytest | Assert response times are within thresholds | `tests/performance/test_book_performance.py` |
| **Load Tests** | Locust | Simulate realistic concurrent users, find bottlenecks | `tests/performance/locustfile.py` |

### Running Tests

**All tests:**
```bash
python -m pytest tests/ -v
```

**Specific test suite:**
```bash
python -m pytest tests/unit/ -v        # Unit tests only
python -m pytest tests/integration/ -v # Integration tests only
python -m pytest tests/performance/test_book_performance.py -v  # Performance assertions
```

**With coverage:**
```bash
pip install pytest-cov
python -m pytest tests/ --cov=routes --cov-report=html
# Open htmlcov/index.html in browser
```

### Performance Testing Details

#### Pytest Performance Tests
Two performance assertions that fail if thresholds are exceeded:

```bash
python -m pytest tests/performance/test_book_performance.py -v
```

- `test_get_books_response_time` — Single request must respond within 200ms
- `test_repeated_requests_throughput` — 50 sequential requests must complete within 2s

#### Locust Load Tests (Recommended)

Locust provides realistic load testing with concurrent users:

```bash
locust -f tests/performance/locustfile.py
```

Open **http://localhost:8089** and configure:
- **Number of users**: 10-500 (depending on test goal)
- **Spawn rate**: 2 users/second
- **Host**: http://localhost:8080 (auto-filled)

**Headless mode (for CI/CD):**
```bash
locust -f tests/performance/locustfile.py --headless -u 100 -r 5 -t 60s --html=report.html
```

**Stress testing (find breaking point):**
```bash
locust -f tests/performance/locustfile.py -u 500 -r 10 --headless
```

Read [LOCUST_GUIDE.md](tests/performance/LOCUST_GUIDE.md) for detailed examples and troubleshooting.

### Test Fixtures

All tests use shared fixtures from `tests/conftest.py`:

- **`app`** — Flask test app with in-memory SQLite database, pre-seeded with 3 books
- **`client`** — Flask test client for making HTTP requests

Fixtures are automatically discovered by Pytest — no imports needed.

---

## Pagination Strategies

The API supports three pagination types:

### 1. Offset-Based Pagination
Most common, simple to implement:
```bash
curl http://localhost:8080/api/books?limit=5&offset=0&pagination_type=offset
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "total": 50,
    "limit": 5,
    "offset": 0,
    "type": "offset"
  }
}
```

### 2. Page-Based Pagination
User-friendly, uses page numbers:
```bash
curl http://localhost:8080/api/books?limit=5&page=2&pagination_type=page
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "total": 50,
    "limit": 5,
    "page": 2,
    "type": "page"
  }
}
```

### 3. Cursor-Based Pagination
Most efficient for large datasets, prevents issues with insertions/deletions:
```bash
curl http://localhost:8080/api/books?limit=5&cursor=10&pagination_type=cursor
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "limit": 5,
    "next_cursor": 15,
    "type": "cursor"
  }
}
```

---

## Database

Uses SQLite with SQLAlchemy ORM.

### Schema

**Books Table:**

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary Key, Auto-increment |
| `title` | String(255) | Required |
| `author` | String(255) | Required |
| `category` | String(100) | Required |
| `available_copies` | Integer | Default: 1 |
| `created_at` | DateTime | Auto-set to now |
| `updated_at` | DateTime | Auto-update |

### Accessing the Database

**Via Flask shell:**
```bash
python
>>> from app import app
>>> from models import db, Book
>>> with app.app_context():
...     books = Book.query.all()
...     print(books)
```

**Inspect with SQLite CLI:**
```bash
sqlite3 library.db
sqlite> SELECT * FROM book;
sqlite> .schema book
```

---

## Configuration

Edit `config.py` to change:

```python
SQLALCHEMY_DATABASE_URI = "sqlite:///library.db"  # Database file
SQLALCHEMY_ECHO = True                           # Log SQL queries
DEBUG = False                                     # Debug mode
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3.3 | Web framework |
| Flask-SQLAlchemy | 3.0.5 | ORM |
| Flasgger | 0.9.7.1 | Swagger/API docs |
| Pytest | 7.4.0 | Testing framework |
| Locust | 2.15.1 | Load testing |

Install all:
```bash
pip install -r requirements.txt
```

---

## Common Tasks

### Add a new test

1. Create a test file in `tests/unit/`, `tests/integration/`, or `tests/performance/`
2. Use the `client` fixture to make requests
3. Use `assert` for verification

```python
def test_example(client):
    response = client.get("/api/books")
    assert response.status_code == 200
    assert "data" in response.get_json()
```

### Add a new endpoint

1. Create route in `routes/`
2. Register blueprint in `app.py` via `apply_routes()`
3. Add unit test to `tests/unit/`
4. Update Swagger spec in `swagger.yml`

### Optimize slow endpoint

1. Run Locust to identify which endpoint is slow
2. Check database queries: add `SQLALCHEMY_ECHO=True` in config and run test
3. Add database indices if needed
4. Run Locust again to verify improvement

### Run tests in CI/CD

```bash
#!/bin/bash
set -e

# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest tests/ -v

# Run load test in headless mode
locust -f tests/performance/locustfile.py --headless -u 50 -r 2 -t 60s --html=report.html

# Check performance thresholds
python -m pytest tests/performance/test_book_performance.py -v
```

---

## Troubleshooting

### "Database is locked"
Multiple processes accessing the same SQLite file. Solution:
- Use in-memory database for tests (already done in `conftest.py`)
- Use a proper database (PostgreSQL) for production

### "Module not found" errors
Ensure virtual environment is activated:
```bash
source venv/bin/activate
```

### Swagger UI not loading
Check that Flasgger is installed and `swagger.yml` exists:
```bash
pip install flasgger
ls Buoi8/swagger.yml
```

### Locust connection refused
Flask app must be running:
```bash
# Terminal 1
python app.py

# Terminal 2
locust -f tests/performance/locustfile.py
```

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Locust Documentation](https://docs.locust.io/)
- [RESTful API Design Best Practices](https://restfulapi.net/)

---

## References

For detailed testing information, see [tests/README.md](tests/README.md).

For quick Locust reference, see [tests/performance/LOCUST_GUIDE.md](tests/performance/LOCUST_GUIDE.md).
