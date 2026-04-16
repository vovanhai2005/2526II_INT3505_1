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
