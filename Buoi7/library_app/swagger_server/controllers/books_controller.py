import connexion
from flask import jsonify
from bson import ObjectId

from swagger_server.database import mongo


def _book_to_dict(book):
    """Convert a MongoDB book document to a JSON-serializable dict."""
    return {
        "id": str(book["_id"]),
        "title": book.get("title"),
        "author": book.get("author"),
        "category": book.get("category"),
        "available_copies": book.get("available_copies", 1)
    }


def get_books(category=None, author=None):  # noqa: E501
    """List all books

     # noqa: E501

    :param category: Filter by category
    :type category: str
    :param author: Filter by author
    :type author: str

    :rtype: List[Book]
    """
    query = {}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if author:
        query["author"] = {"$regex": author, "$options": "i"}

    books = mongo.db.books.find(query)
    return jsonify([_book_to_dict(b) for b in books]), 200


def create_book(body):  # noqa: E501
    """Create a new book

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        data = connexion.request.get_json()
    else:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ("title", "author", "category")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    book_doc = {
        "title": data["title"],
        "author": data["author"],
        "category": data["category"],
        "available_copies": data.get("available_copies", 1)
    }
    result = mongo.db.books.insert_one(book_doc)
    book_doc["_id"] = result.inserted_id

    return jsonify(_book_to_dict(book_doc)), 201


def api_books_book_id_get(book_id):  # noqa: E501
    """Get book by ID

     # noqa: E501

    :param book_id: Unique book identifier
    :type book_id: int

    :rtype: Book
    """
    try:
        book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    except Exception:
        return jsonify({"error": "Invalid book ID format"}), 400

    if not book:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(_book_to_dict(book)), 200


def api_books_book_id_put(body, book_id):  # noqa: E501
    """Update a book

     # noqa: E501

    :param body:
    :type body: dict | bytes
    :param book_id: Unique book identifier
    :type book_id: int

    :rtype: None
    """
    if connexion.request.is_json:
        data = connexion.request.get_json()
    else:
        return jsonify({"error": "Request body must be JSON"}), 400

    try:
        oid = ObjectId(book_id)
    except Exception:
        return jsonify({"error": "Invalid book ID format"}), 400

    update_fields = {}
    for field in ("title", "author", "category", "available_copies"):
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    result = mongo.db.books.update_one({"_id": oid}, {"$set": update_fields})
    if result.matched_count == 0:
        return jsonify({"error": "Book not found"}), 404

    book = mongo.db.books.find_one({"_id": oid})
    return jsonify(_book_to_dict(book)), 200


def api_books_book_id_delete(book_id):  # noqa: E501
    """Delete a book

     # noqa: E501

    :param book_id: Unique book identifier
    :type book_id: int

    :rtype: None
    """
    try:
        oid = ObjectId(book_id)
    except Exception:
        return jsonify({"error": "Invalid book ID format"}), 400

    result = mongo.db.books.delete_one({"_id": oid})
    if result.deleted_count == 0:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({"message": "Book deleted"}), 200