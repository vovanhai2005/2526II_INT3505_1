import time


def test_get_books_response_time(client):
    """GET /api/books must respond within 200ms."""
    start = time.perf_counter()
    resp = client.get("/api/books")
    elapsed = time.perf_counter() - start

    assert resp.status_code == 200
    assert elapsed < 0.2, f"Response too slow: {elapsed:.3f}s (limit 0.200s)"


def test_repeated_requests_throughput(client):
    """50 sequential requests to GET /api/books must all complete within 2s."""
    start = time.perf_counter()
    for _ in range(50):
        resp = client.get("/api/books")
        assert resp.status_code == 200
    elapsed = time.perf_counter() - start

    assert elapsed < 2.0, f"50 requests took {elapsed:.3f}s (limit 2.000s)"
