def test_get_books(client):
    resp = client.get("/api/books")
    assert resp.status_code == 200
    assert len(resp.get_json()["data"]) == 3


def test_get_book_by_id(client):
    resp = client.get("/api/books/1")
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Clean Code"


def test_create_book(client):
    resp = client.post("/api/books", json={
        "title": "1984",
        "author": "George Orwell",
        "category": "Dystopian",
    })
    assert resp.status_code == 201
    assert resp.get_json()["title"] == "1984"


def test_update_book(client):
    resp = client.put("/api/books/1", json={"title": "Clean Code 2nd Ed"})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Clean Code 2nd Ed"


def test_delete_book(client):
    resp = client.delete("/api/books/1")
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "Book deleted"
