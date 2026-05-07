# Locust Load Testing Guide

Quick reference for running performance tests with Locust on the Book API.

## Prerequisites

```bash
# Install Locust
pip install locust

# Or install from requirements.txt
pip install -r requirements.txt
```

## Quick Start (5 minutes)

### Terminal 1: Start the Flask app

```bash
cd Buoi8
python app.py
# App runs on http://localhost:8080
```

### Terminal 2: Start Locust

```bash
cd Buoi8
locust -f tests/performance/locustfile.py
# Web UI runs on http://localhost:8089
```

### Browser: Open web UI

1. Open **http://localhost:8089**
2. Enter:
   - **Number of users**: `10`
   - **Spawn rate**: `2`
3. Click **Start swarming**

Watch real-time metrics:
- **RPS** (Requests Per Second)
- **Response times** (Median, 95%ile, 99%ile)
- **Failure count**

---

## Common Commands

### Interactive mode (web UI)

```bash
locust -f tests/performance/locustfile.py
```

### Headless mode (terminal output)

```bash
locust -f tests/performance/locustfile.py --headless -u 50 -r 5 -t 60s
```

Parameters:
- `-u 50`: 50 concurrent users
- `-r 5`: spawn 5 users per second
- `-t 60s`: run for 60 seconds (can be `5m` for 5 minutes)

### Generate HTML report

```bash
locust -f tests/performance/locustfile.py --headless -u 100 -r 5 -t 120s --html=report.html
```

Report will be saved as `report.html` in the current directory.

### Stress test (find breaking point)

```bash
locust -f tests/performance/locustfile.py -u 500 -r 10 --headless
```

Watch when response times spike or failures appear.

---

## Understanding Results

| Metric | Meaning |
|--------|---------|
| **Requests** | Total HTTP requests made |
| **Failures** | Number of requests that failed (5xx, 4xx, timeout) |
| **Median** | 50% of requests are faster, 50% slower |
| **95%ile** | 95% of requests are faster than this (SLA threshold) |
| **99%ile** | 99% of requests are faster (worst-case scenario) |
| **RPS** | Requests per second (throughput) |

**Example:**
```
GET /api/books
- 1000 requests
- 2 failures (0.2%)
- Median: 45ms
- 95%ile: 120ms
- RPS: 8.3
```

This means:
- API handled 1000 requests with 99.8% success rate
- Half the requests returned in 45ms
- 95% of requests completed within 120ms
- System is processing ~8 requests per second

---

## Test Scenarios

### 1. Check baseline (normal load)

```bash
locust -f tests/performance/locustfile.py -u 10 -r 2 --headless -t 60s --html=baseline.html
```

### 2. Find the limit (stress test)

```bash
locust -f tests/performance/locustfile.py -u 500 -r 10 --headless
```

Watch when errors spike or response times exceed thresholds.

### 3. Simulate real traffic

```bash
locust -f tests/performance/locustfile.py -u 50 -r 2 --headless -t 5m
```

### 4. Compare before/after optimization

```bash
# Before optimization
locust -f tests/performance/locustfile.py -u 50 -r 2 --html=before.html

# Make code changes...

# After optimization
locust -f tests/performance/locustfile.py -u 50 -r 2 --html=after.html

# Compare before.html vs after.html
```

---

## Troubleshooting

**Error: "Connection refused"**
- Is Flask running? Check `http://localhost:8080`
- Restart: `python app.py`

**Error: "AssertionError: No taskset found"**
- Make sure you're in the `Buoi8` directory
- Check the app imports work: `python -c "from app import app"`

**Slow response times (>1s)**
- Reduce spawn rate: `locust -f tests/performance/locustfile.py -r 1`
- Check if database is bottleneck: run `FLASK_ENV=development python app.py` and check logs
- Monitor system resources: `top` or `htop`

**No failures but want to test error handling**
- Kill the Flask app and see how Locust handles connection errors
- Try hitting a wrong endpoint: modify `locustfile.py` to hit `/api/invalid`

---

## Files

- **`locustfile.py`** — Load test definition (users, tasks, behavior)
- **`test_book_performance.py`** — Traditional pytest performance tests (response time assertions)
- **`../README.md`** — Full testing documentation

---

## Next Steps

1. ✅ Run baseline: `locust -f tests/performance/locustfile.py -u 10 -r 2 --html=baseline.html`
2. 🔍 Identify bottleneck (check `baseline.html`)
3. 🔧 Optimize code (add indexing, caching, query optimization)
4. 📊 Compare: `locust -f tests/performance/locustfile.py -u 10 -r 2 --html=optimized.html`
5. 📈 Track improvement in metrics

---

## Resources

- [Locust Documentation](https://docs.locust.io/)
- [Locust GitHub](https://github.com/locustio/locust)
- [Load Testing Best Practices](https://docs.locust.io/en/stable/best-practices.html)
