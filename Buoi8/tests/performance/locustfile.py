"""
Load testing for Book API using Locust.

Run with:
  locust -f locustfile.py

Access the web UI at http://localhost:8089
"""

import os
import sys
from locust import HttpUser, task, between, events

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app import app as flask_app
from models import db, Book


class BookAPIUser(HttpUser):
    """Simulates a user performing various Book API operations."""

    wait_time = between(0.5, 2.0)

    def on_start(self):
        """Called when a simulated user starts."""
        self.book_ids = []

    @task(3)
    def list_books(self):
        """List all books with offset pagination."""
        with self.client.get(
            "/api/books",
            params={"limit": 10, "offset": 0, "pagination_type": "offset"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                try:
                    data = response.json()
                    if "data" in data and len(data["data"]) > 0:
                        self.book_ids = [book["id"] for book in data["data"]]
                except ValueError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Expected 200, got {response.status_code}")

    @task(2)
    def get_book_by_id(self):
        """Get a specific book by ID."""
        if not self.book_ids:
            return

        book_id = self.book_ids[0]
        with self.client.get(
            f"/api/books/{book_id}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Expected 200, got {response.status_code}")

    @task(2)
    def filter_books_by_category(self):
        """Filter books by category."""
        categories = ["Programming", "Fantasy", "Sci-Fi"]
        category = categories[hash(self) % len(categories)]

        with self.client.get(
            "/api/books",
            params={"category": category, "limit": 10},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Expected 200, got {response.status_code}")

    @task(1)
    def create_book(self):
        """Create a new book."""
        import random
        payload = {
            "title": f"New Book {random.randint(1000, 9999)}",
            "author": "Test Author",
            "category": "Programming",
            "available_copies": 5
        }

        with self.client.post(
            "/api/books",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
                try:
                    data = response.json()
                    if "id" in data:
                        self.book_ids.append(data["id"])
                except ValueError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Expected 201, got {response.status_code}")

    @task(1)
    def update_book(self):
        """Update an existing book."""
        if not self.book_ids:
            return

        book_id = self.book_ids[0]
        payload = {
            "title": f"Updated Book",
            "available_copies": 10
        }

        with self.client.put(
            f"/api/books/{book_id}",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Expected 200, got {response.status_code}")

    @task(1)
    def delete_book(self):
        """Delete a book."""
        if not self.book_ids or len(self.book_ids) < 2:
            return

        book_id = self.book_ids.pop()

        with self.client.delete(
            f"/api/books/{book_id}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Expected 200, got {response.status_code}")


@events.test_start.add_listener
def on_test_start(**kwargs):
    """Initialize the test environment with seed data."""
    with flask_app.app_context():
        db.create_all()

        existing_books = Book.query.count()
        if existing_books == 0:
            seed_books = [
                Book(title="Clean Code", author="Robert Martin", category="Programming", available_copies=3),
                Book(title="The Hobbit", author="J.R.R. Tolkien", category="Fantasy", available_copies=2),
                Book(title="Dune", author="Frank Herbert", category="Sci-Fi", available_copies=5),
                Book(title="Python Crash Course", author="Eric Matthes", category="Programming", available_copies=4),
                Book(title="The Fellowship of the Ring", author="J.R.R. Tolkien", category="Fantasy", available_copies=3),
            ]
            db.session.add_all(seed_books)
            db.session.commit()


@events.test_stop.add_listener
def on_test_stop(**kwargs):
    """Clean up after test."""
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """Final cleanup."""
    pass
