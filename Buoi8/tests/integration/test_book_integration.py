def test_full_crud_lifecycle(client):
    """Create → read → update → delete a book and verify state at each step."""
    # Create
    create_resp = client.post("/api/books", json={
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "category": "Dystopian",
        "available_copies": 2,
    })
    assert create_resp.status_code == 201
    book_id = create_resp.get_json()["id"]

    # Read — book appears in the list
    list_resp = client.get("/api/books")
    assert list_resp.status_code == 200
    ids = [b["id"] for b in list_resp.get_json()["data"]]
    assert book_id in ids

    # Update
    update_resp = client.put(f"/api/books/{book_id}", json={"available_copies": 10})
    assert update_resp.status_code == 200
    assert update_resp.get_json()["available_copies"] == 10

    # Verify update persisted via GET
    get_resp = client.get(f"/api/books/{book_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["available_copies"] == 10

    # Delete
    delete_resp = client.delete(f"/api/books/{book_id}")
    assert delete_resp.status_code == 200

    # Verify deletion — book no longer accessible
    get_after_delete = client.get(f"/api/books/{book_id}")
    assert get_after_delete.status_code == 404

    # Verify deletion — book absent from the list
    list_after_delete = client.get("/api/books")
    ids_after = [b["id"] for b in list_after_delete.get_json()["data"]]
    assert book_id not in ids_after


def test_create_then_filter(client):
    """Books created via POST are immediately visible through filtered GET requests."""
    client.post("/api/books", json={
        "title": "Neuromancer",
        "author": "William Gibson",
        "category": "Cyberpunk",
        "available_copies": 1,
    })
    client.post("/api/books", json={
        "title": "Snow Crash",
        "author": "Neal Stephenson",
        "category": "Cyberpunk",
        "available_copies": 3,
    })

    resp = client.get("/api/books?category=Cyberpunk")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 2
    titles = {b["title"] for b in data}
    assert titles == {"Neuromancer", "Snow Crash"}


def test_pagination_reflects_deletions(client):
    """Total count returned by pagination decreases after a book is deleted."""
    initial_resp = client.get("/api/books")
    initial_total = initial_resp.get_json()["pagination"]["total"]

    # Delete the first seeded book
    client.delete("/api/books/1")

    updated_resp = client.get("/api/books")
    updated_total = updated_resp.get_json()["pagination"]["total"]

    assert updated_total == initial_total - 1
