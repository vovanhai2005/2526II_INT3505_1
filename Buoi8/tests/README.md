# Running Tests — Book API

This directory contains three kinds of tests for the Book resource API.

```
tests/
├── conftest.py                          # Shared fixtures (app + client)
├── unit/
│   └── test_book_unit.py               # 5 unit tests (one per endpoint)
├── integration/
│   └── test_book_integration.py        # 3 integration tests (multi-step flows)
└── performance/
    └── test_book_performance.py        # 2 performance tests (timing thresholds)
```

---

## Prerequisites

### 1. Activate the virtual environment

From the project root (`2526II_INT3505_1/`):

```bash
source venv/bin/activate
```

> On Windows: `venv\Scripts\activate`

### 2. Install dependencies (first time only)

```bash
pip install flask flask-sqlalchemy pytest
```

### 3. Navigate to the app directory

```bash
cd Buoi8
```

All `pytest` commands below assume you are inside the `Buoi8/` directory.

---

## Running All Tests

```bash
python -m pytest tests/
```

Expected output:

```
10 passed in ~0.2s
```

Add `-v` for verbose output showing each test name:

```bash
python -m pytest tests/ -v
```

---

## Unit Tests

**Location:** `tests/unit/test_book_unit.py`

**Purpose:** Verify that each API endpoint returns the correct HTTP status code and response body in isolation. Each test covers exactly one endpoint with a valid, happy-path request.

| Test | Endpoint |
|------|----------|
| `test_get_books` | `GET /api/books` |
| `test_get_book_by_id` | `GET /api/books/<id>` |
| `test_create_book` | `POST /api/books` |
| `test_update_book` | `PUT /api/books/<id>` |
| `test_delete_book` | `DELETE /api/books/<id>` |

### Run unit tests only

```bash
python -m pytest tests/unit/ -v
```

### Run a single unit test

```bash
python -m pytest tests/unit/test_book_unit.py::test_create_book -v
```

---

## Integration Tests

**Location:** `tests/integration/test_book_integration.py`

**Purpose:** Verify that multiple endpoints work correctly together across a full request sequence. These tests simulate realistic workflows where one operation's output feeds into the next.

| Test | What it covers |
|------|----------------|
| `test_full_crud_lifecycle` | Create → Read → Update → Delete a single book and verify state after each step |
| `test_create_then_filter` | Create books via `POST`, then confirm they appear in filtered `GET` results |
| `test_pagination_reflects_deletions` | Check that `pagination.total` decreases after a `DELETE` |

### Run integration tests only

```bash
python -m pytest tests/integration/ -v
```

### Run a single integration test

```bash
python -m pytest tests/integration/test_book_integration.py::test_full_crud_lifecycle -v
```

---

## Performance Tests

**Location:** `tests/performance/test_book_performance.py`

**Purpose:** Assert that endpoints respond within acceptable time thresholds. Tests fail if the response is too slow, catching regressions introduced by slow queries or expensive logic.

| Test | What it measures | Threshold |
|------|-----------------|-----------|
| `test_get_books_response_time` | Single `GET /api/books` wall-clock time | < 200ms |
| `test_repeated_requests_throughput` | 50 sequential `GET /api/books` requests total time | < 2s |

### Run performance tests only

```bash
python -m pytest tests/performance/ -v
```

### Run a single performance test

```bash
python -m pytest tests/performance/test_book_performance.py::test_repeated_requests_throughput -v
```

---

## Useful Options

| Flag | Description |
|------|-------------|
| `-v` | Verbose — show each test name and result |
| `-q` | Quiet — show only summary line |
| `-s` | Show `print()` output from tests |
| `-x` | Stop immediately on first failure |
| `--tb=short` | Show a shorter traceback on failure |
| `-W ignore` | Suppress deprecation warnings |
| `--no-header` | Hide the pytest version header |

Example combining flags:

```bash
python -m pytest tests/ -v -x --tb=short
```

---

## How Fixtures Work

All three test suites share the fixtures defined in `tests/conftest.py`. Pytest discovers this file automatically — no imports needed in the test files.

**`app` fixture** — Creates an isolated Flask app backed by an **in-memory SQLite database** (`sqlite:///:memory:`). The database is seeded with 3 books before each test and completely destroyed afterwards, so tests never affect each other or the real `library.db` file.

**`client` fixture** — Wraps the app in a Flask test client, enabling HTTP requests (`GET`, `POST`, `PUT`, `DELETE`) without starting a real server.
