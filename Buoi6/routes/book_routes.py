from flask import Blueprint, jsonify, request
from models import Book, db
from utils.jwt import require_jwt

book_bp = Blueprint("book_bp", __name__, url_prefix="/api/books")


@book_bp.route("", methods=["GET"])
@require_jwt()
def get_books(claims):
    """List all books, with optional filtering by category or author."""
    category = request.args.get("category")
    author = request.args.get("author")

    query = Book.query
    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))

    books = query.all()
    return jsonify([b.validate_response() for b in books]), 200


@book_bp.route("/<int:book_id>", methods=["GET"])
@require_jwt()
def get_book(claims, book_id):
    """Get a single book by ID."""
    book = Book.query.get_or_404(book_id, description="Book not found")
    return jsonify(book.validate_response()), 200


@book_bp.route("", methods=["POST"])
@require_jwt()
def create_book(claims):
    """Create a new book."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ("title", "author", "category")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    book = Book(
        title=data["title"],
        author=data["author"],
        category=data["category"],
        available_copies=data.get("available_copies", 1),
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.validate_response()), 201


@book_bp.route("/<int:book_id>", methods=["PUT"])
@require_jwt()
def update_book(claims, book_id):
    """Update an existing book."""
    book = Book.query.get_or_404(book_id, description="Book not found")
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.category = data.get("category", book.category)
    book.available_copies = data.get("available_copies", book.available_copies)
    db.session.commit()
    return jsonify(book.validate_response()), 200


@book_bp.route("/<int:book_id>", methods=["DELETE"])
@require_jwt()
def delete_book(claims, book_id):
    """Delete a book."""
    book = Book.query.get_or_404(book_id, description="Book not found")
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"}), 200
