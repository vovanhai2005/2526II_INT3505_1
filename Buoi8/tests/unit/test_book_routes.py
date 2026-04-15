import os
import sys

import pytest
from flask import Flask

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import Book, db
from routes.book_routes import book_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True

    db.init_app(app)
    app.register_blueprint(book_bp)

    with app.app_context():
        db.create_all()
        db.session.add_all([
            Book(title="Clean Code", author="Robert Martin", category="Programming", available_copies=3),
            Book(title="The Hobbit", author="J.R.R. Tolkien", category="Fantasy", available_copies=2),
            Book(title="Dune", author="Frank Herbert", category="Sci-Fi", available_copies=5),
        ])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_books_offset_pagination(client):
    resp = client.get("/api/books?limit=2&offset=0")
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["data"]) == 2
    assert body["pagination"]["total"] == 3
    assert body["pagination"]["type"] == "offset"


def test_get_books_page_pagination(client):
    resp = client.get("/api/books?pagination_type=page&limit=2&page=2")
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["data"]) == 1
    assert body["pagination"]["page"] == 2


def test_get_books_cursor_pagination(client):
    resp = client.get("/api/books?pagination_type=cursor&limit=2")
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["data"]) == 2
    assert body["pagination"]["next_cursor"] is not None


def test_get_books_filter_by_category(client):
    resp = client.get("/api/books?category=Fantasy")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 1
    assert data[0]["title"] == "The Hobbit"


def test_get_books_filter_by_author(client):
    resp = client.get("/api/books?author=Herbert")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 1
    assert data[0]["author"] == "Frank Herbert"


def test_get_books_invalid_pagination_type(client):
    resp = client.get("/api/books?pagination_type=invalid")
    assert resp.status_code == 400


def test_get_book_by_id(client):
    resp = client.get("/api/books/1")
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Clean Code"


def test_get_book_not_found(client):
    resp = client.get("/api/books/999")
    assert resp.status_code == 404


def test_create_book(client):
    payload = {
        "title": "1984",
        "author": "George Orwell",
        "category": "Dystopian",
        "available_copies": 4,
    }
    resp = client.post("/api/books", json=payload)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "1984"
    assert body["available_copies"] == 4


def test_create_book_missing_fields(client):
    resp = client.post("/api/books", json={"title": "Incomplete"})
    assert resp.status_code == 400
    assert "Missing fields" in resp.get_json()["error"]


def test_create_book_no_body(client):
    resp = client.post("/api/books", json=None, content_type="application/json")
    assert resp.status_code == 400


def test_update_book(client):
    resp = client.put("/api/books/1", json={"title": "Clean Code 2nd Ed"})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Clean Code 2nd Ed"


def test_update_book_not_found(client):
    resp = client.put("/api/books/999", json={"title": "Nope"})
    assert resp.status_code == 404


def test_delete_book(client):
    resp = client.delete("/api/books/1")
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "Book deleted"

    follow_up = client.get("/api/books/1")
    assert follow_up.status_code == 404


def test_delete_book_not_found(client):
    resp = client.delete("/api/books/999")
    assert resp.status_code == 404
