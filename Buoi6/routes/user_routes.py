from flask import Blueprint, jsonify, request
from models import User, db
from utils.jwt import require_jwt, create_access_token

user_bp = Blueprint("user_bp", __name__, url_prefix="/api/users")


@user_bp.route("/login", methods=["POST"])
def login():
    """Login endpoint to retrieve a JWT token."""
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Missing email"}), 400
    user = User.query.filter_by(email=data["email"]).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    token = create_access_token(user.id, "user")
    return jsonify({"token": token}), 200


@user_bp.route("", methods=["GET"])
@require_jwt()
def get_users(claims):
    """List all users."""
    users = User.query.all()
    return jsonify([u.validate_response() for u in users]), 200


@user_bp.route("/<int:user_id>", methods=["GET"])
@require_jwt()
def get_user(claims, user_id):
    """Get a single user by ID."""
    user = User.query.get_or_404(user_id, description="User not found")
    return jsonify(user.validate_response()), 200


@user_bp.route("", methods=["POST"])
def create_user():
    """Create a new user. (No JWT required to sign up)"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ("name", "email")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.validate_response()), 201


@user_bp.route("/<int:user_id>", methods=["PUT"])
@require_jwt()
def update_user(claims, user_id):
    """Update an existing user."""
    user = User.query.get_or_404(user_id, description="User not found")
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    user.name = data.get("name", user.name)
    if "email" in data and data["email"] != user.email:
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already exists"}), 409
        user.email = data["email"]

    db.session.commit()
    return jsonify(user.validate_response()), 200


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@require_jwt()
def delete_user(claims, user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id, description="User not found")
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200
