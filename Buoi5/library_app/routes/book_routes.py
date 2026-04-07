from flask import Blueprint, jsonify, request

from models import Book, db

book_bp = Blueprint("book_bp", __name__, url_prefix="/api/books")


@book_bp.route("", methods=["GET"])
def get_books():
    """List all books, with optional filtering by category or author."""
    category = request.args.get("category")
    author = request.args.get("author")
    limit = int(request.args.get("limit", 10))
    pagination_type = request.args.get("pagination_type", "offset") # offset, page, cursor

    query = Book.query
    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))

    if pagination_type == "offset":
        offset = int(request.args.get("offset", 0))
        total = query.count()
        books = query.offset(offset).limit(limit).all()
        return jsonify({
            "data": [b.validate_response() for b in books],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "type": "offset"
            }
        }), 200

    elif pagination_type == "page":
        page = int(request.args.get("page", 1))
        offset = (page - 1) * limit
        total = query.count()
        books = query.offset(offset).limit(limit).all()
        return jsonify({
            "data": [b.validate_response() for b in books],
            "pagination": {
                "total": total,
                "limit": limit,
                "page": page,
                "type": "page"
            }
        }), 200

    elif pagination_type == "cursor":
        cursor = request.args.get("cursor") # Use the id of the last seen item
        if cursor:
            query = query.filter(Book.id > int(cursor))
        
        books = query.order_by(Book.id.asc()).limit(limit).all()
        next_cursor = books[-1].id if books else None
        
        return jsonify({
            "data": [b.validate_response() for b in books],
            "pagination": {
                "limit": limit,
                "next_cursor": next_cursor,
                "type": "cursor"
            }
        }), 200

    return jsonify({"error": "Invalid pagination type"}), 400


@book_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """Get a single book by ID."""
    book = Book.query.get_or_404(book_id, description="Book not found")
    return jsonify(book.validate_response()), 200


@book_bp.route("", methods=["POST"])
def create_book():
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
def update_book(book_id):
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
def delete_book(book_id):
    """Delete a book."""
    book = Book.query.get_or_404(book_id, description="Book not found")
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"}), 200
