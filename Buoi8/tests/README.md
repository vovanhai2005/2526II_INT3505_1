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

### Pytest-based Performance Tests

**Location:** `tests/performance/test_book_performance.py`

**Purpose:** Assert that endpoints respond within acceptable time thresholds. Tests fail if the response is too slow, catching regressions introduced by slow queries or expensive logic.

| Test | What it measures | Threshold |
|------|-----------------|-----------|
| `test_get_books_response_time` | Single `GET /api/books` wall-clock time | < 200ms |
| `test_repeated_requests_throughput` | 50 sequential `GET /api/books` requests total time | < 2s |

#### Run performance tests only

```bash
python -m pytest tests/performance/ -v
```

#### Run a single performance test

```bash
python -m pytest tests/performance/test_book_performance.py::test_repeated_requests_throughput -v
```

---

### Load Testing with Locust

**Location:** `tests/performance/locustfile.py`

**Purpose:** Simulate realistic concurrent load on the API and identify bottlenecks, measure response times under stress, and track throughput. Locust is ideal for load testing, stress testing, and understanding system behavior under traffic.

#### What is Locust?

Locust is an open-source load testing tool written in Python. It allows you to:
- Simulate multiple concurrent users hitting your API
- Define realistic user behavior (task sequences)
- Monitor response times, throughput, and failure rates in real-time
- Generate HTML reports with detailed statistics
- Identify performance bottlenecks before production

#### Installation

Add Locust to your dependencies:

```bash
pip install locust
```

#### Quick Start

1. **Start the Flask app** (in one terminal):

```bash
cd Buoi8
python app.py
```

The app will run on `http://localhost:8080`.

2. **Start Locust** (in another terminal):

```bash
cd Buoi8
locust -f tests/performance/locustfile.py
```

3. **Open the web UI**:

Navigate to `http://localhost:8089` in your browser.

4. **Configure the test**:

- **Host**: `http://localhost:8080` (auto-populated based on app)
- **Number of users**: Start with 10, increase to 100 for stress testing
- **Spawn rate**: 2 (new users per second)
- **Run time**: Leave empty to run until you stop it manually

5. **Start the test**:

Click the "Start swarming" button. Locust will:
- Spawn users gradually at the specified spawn rate
- Each user waits 0.5-2 seconds between requests
- Tasks are weighted: listing books (3) > filtering & getting by ID (2 each) > create/update/delete (1 each)
- Real-time graphs show response times, RPS (requests per second), and failure rates

#### Understanding the Test Behavior

**User Lifecycle:**

Each simulated user follows this pattern:
1. Starts and fetches the initial list of books
2. Waits 0.5-2 seconds (random)
3. Picks a random task based on weights:
   - **List books (30%)** — `GET /api/books` with offset pagination
   - **Get book by ID (20%)** — `GET /api/books/{id}` for a book from the list
   - **Filter by category (20%)** — `GET /api/books?category=X`
   - **Create book (10%)** — `POST /api/books` with test data
   - **Update book (10%)** — `PUT /api/books/{id}` to modify a book
   - **Delete book (10%)** — `DELETE /api/books/{id}` to remove a book
4. Repeats step 2-3 indefinitely

**Task Weights Explained:**

Weights reflect realistic API usage. Most traffic is reads (list, filter, get), fewer writes (create, update, delete). The distribution can be adjusted in `locustfile.py` by changing the `@task(N)` decorator value.

#### Command-Line Options

```bash
# Run in headless mode (no web UI, all stats in terminal)
locust -f tests/performance/locustfile.py --headless -u 50 -r 2 -t 60s

# Run with custom host
locust -f tests/performance/locustfile.py --host=http://localhost:8080

# Generate HTML report
locust -f tests/performance/locustfile.py --headless -u 100 -r 5 -t 120s --html=report.html

# Run for specific duration (e.g., 5 minutes)
locust -f tests/performance/locustfile.py -t 5m

# Set custom CSV output for statistics
locust -f tests/performance/locustfile.py --csv=results
```

#### Interpreting Results

**Web UI Metrics:**

- **Type**: HTTP method (GET, POST, PUT, DELETE)
- **Name**: Endpoint path
- **# requests**: Total number of requests made
- **# failures**: Number of failed requests
- **Median**: Median response time (ms)
- **95%ile**: 95th percentile response time (ms) — most requests under this time
- **99%ile**: 99th percentile response time (ms) — good for understanding worst-case
- **Average**: Mean response time (ms)
- **Min**: Fastest response time (ms)
- **Max**: Slowest response time (ms)
- **Average size**: Average response body size (bytes)
- **RPS**: Requests per second (throughput)

**Example interpretation:**
```
GET /api/books | 500 requests | 0 failures | Median: 45ms | 95%ile: 120ms | RPS: 8.3
```
This endpoint handled 500 requests with no failures. Half of requests returned in under 45ms, and 95% in under 120ms. The system is handling 8.3 requests per second on average.

**Failure Reasons:**

If failures occur, check the "Failures" tab for details:
- **5xx errors**: Server-side problems (query issues, missing data)
- **4xx errors**: Client-side problems (invalid request format)
- **Connection errors**: Server not responding (crash, overload)

#### Common Issues and Troubleshooting

**Issue: "ConnectionError" or "Connection refused"**

The Flask app may have crashed or isn't running. Check:
```bash
# Is the app running?
ps aux | grep "python app.py"

# Restart the app
python app.py
```

**Issue: "No matching users"**

Locust can't find the app. Ensure:
- Flask app is running on `http://localhost:8080`
- Host field in web UI matches the app's address
- No firewall blocking localhost traffic

**Issue: Response times are slow (>500ms)**

Possible causes:
- Database queries are expensive (check queries in `book_routes.py`)
- Not enough system resources (CPU, memory)
- Spawn rate is too high for the machine (lower spawn rate to 1-2)
- App is hitting its connection pool limit (increase pool size in config)

**Issue: "Failed to open HTML report"**

Ensure you have write permissions in the current directory:
```bash
cd Buoi8
locust -f tests/performance/locustfile.py --html=report.html
# report.html will be created here
```

#### Advanced Scenarios

**Simulate peak traffic (100 users):**

```bash
locust -f tests/performance/locustfile.py -u 100 -r 5 --headless -t 5m
```

This spawns 100 users at 5 users/second, runs for 5 minutes, prints results to terminal.

**Stress test (ramp up to failure):**

```bash
locust -f tests/performance/locustfile.py -u 500 -r 10 --headless
```

Spawn 500 users at 10/second. Watch when response times spike or errors appear. This identifies the system's breaking point.

**Baseline comparison:**

```bash
# Run 1: baseline (10 users)
locust -f tests/performance/locustfile.py -u 10 -r 2 --html=baseline.html

# Run 2: after optimization (10 users)
locust -f tests/performance/locustfile.py -u 10 -r 2 --html=optimized.html

# Compare the two reports
```

#### Customizing User Behavior

Edit `tests/performance/locustfile.py` to change:

**1. Adjust task weights:**

```python
@task(5)  # Higher number = more frequent
def list_books(self):
    ...

@task(1)  # Lower number = less frequent
def delete_book(self):
    ...
```

**2. Change wait time between requests:**

```python
# Current: random 0.5-2 seconds
wait_time = between(0.5, 2.0)

# Options:
# wait_time = constant(1)  # Always 1 second
# wait_time = constant_pacing(1)  # 1 second start-to-start
# wait_time = random_between(0, 5)  # 0-5 seconds
```

**3. Add new user behavior:**

```python
@task(2)
def search_books_by_author(self):
    """Search for books by author."""
    authors = ["Robert Martin", "J.R.R. Tolkien", "Frank Herbert"]
    author = authors[hash(self) % len(authors)]
    
    with self.client.get(
        "/api/books",
        params={"author": author},
        catch_response=True
    ) as response:
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Expected 200, got {response.status_code}")
```

#### Best Practices

1. **Run Locust on a separate machine** from the app for accurate measurements (avoid local interference).
2. **Warm up the app** before heavy load (let it run for 1-2 minutes with low concurrency).
3. **Monitor system resources** (CPU, memory, disk I/O) while running tests.
4. **Test in stages** — start small (10 users), then double (20, 40, 80) to find the breaking point.
5. **Record baselines** — save results before and after optimizations for comparison.
6. **Use realistic think time** — configure wait times that match real user behavior.
7. **Test all endpoints** — ensure critical paths are covered in task weights.

#### Integrating with CI/CD

To run load tests in your pipeline with pass/fail criteria:

```python
# In locustfile.py, add assertions
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Fail if 95%ile response time exceeds threshold."""
    for endpoint, stats in environment.stats.entries.items():
        p95 = stats.get_response_time_percentile(0.95)
        if p95 > 200:  # 200ms threshold
            raise AssertionError(f"{endpoint} 95%ile: {p95}ms exceeds 200ms limit")
```

Then run:
```bash
locust -f tests/performance/locustfile.py --headless -u 50 -r 2 -t 60s
```

If assertions fail, exit code will be non-zero, failing the CI job.

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
