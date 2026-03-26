from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from models import Book, Loan, User, db

loan_bp = Blueprint("loan_bp", __name__, url_prefix="/api/loans")


@loan_bp.route("", methods=["GET"])
def get_loans():
    """List all loans. Optionally filter by user_id or active-only."""
    user_id = request.args.get("user_id", type=int)
    active_only = request.args.get("active", "").lower() == "true"

    query = Loan.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    if active_only:
        query = query.filter(Loan.return_date.is_(None))

    loans = query.all()
    return jsonify([l.validate_response() for l in loans]), 200


@loan_bp.route("/<int:loan_id>", methods=["GET"])
def get_loan(loan_id):
    """Get a single loan by ID."""
    loan = Loan.query.get_or_404(loan_id, description="Loan not found")
    return jsonify(loan.validate_response()), 200


@loan_bp.route("/borrow", methods=["POST"])
def borrow_book():
    """Borrow a book: creates a Loan record and decrements available_copies."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ("user_id", "book_id")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    user = User.query.get(data["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    book = Book.query.get(data["book_id"])
    if not book:
        return jsonify({"error": "Book not found"}), 404

    if book.available_copies < 1:
        return jsonify({"error": "No copies available"}), 400

    # Check if user already has an active loan for this book
    existing = Loan.query.filter_by(
        user_id=user.id, book_id=book.id, return_date=None
    ).first()
    if existing:
        return jsonify({"error": "User already has this book on loan"}), 409

    book.available_copies -= 1
    loan = Loan(user_id=user.id, book_id=book.id)
    db.session.add(loan)
    db.session.commit()

    return jsonify(loan.validate_response()), 201


@loan_bp.route("/<int:loan_id>/return", methods=["POST"])
def return_book(loan_id):
    """Return a borrowed book: sets return_date and increments available_copies."""
    loan = Loan.query.get_or_404(loan_id, description="Loan not found")

    if loan.return_date is not None:
        return jsonify({"error": "Book has already been returned"}), 400

    loan.return_date = datetime.now(timezone.utc)
    loan.book.available_copies += 1
    db.session.commit()

    return jsonify(loan.validate_response()), 200
