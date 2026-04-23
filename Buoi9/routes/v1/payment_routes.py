"""
Payment API — Version 1 (DEPRECATED)

Mounted at: /api/v1/payments
Status:     Deprecated — sunset date 2026-12-31
Successor:  /api/v2/payments

Breaking changes introduced in v2 that this version does NOT support:
  - amount is a float (dollars); v2 uses integer cents
  - card exposed as top-level card_number_last4; v2 nests it inside payment_method
  - status values are "pending" | "success" | "failed" only; v2 adds "processing" and "refunded"
  - no idempotency_key, metadata, description, or updated_at fields
  - no refund endpoint
"""
import json

from flask import Blueprint, current_app, jsonify, request

from middleware.deprecation import inject_deprecation_warning
from models import Payment, db

payment_v1_bp = Blueprint("payment_v1", __name__, url_prefix="/api/v1/payments")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _v1_response(data: dict, status_code: int = 200):
    """Wrap data with a deprecation warning and return a JSON response."""
    sunset = current_app.config.get("API_V1_SUNSET_DATE", "2026-12-31")
    return jsonify(inject_deprecation_warning(data, sunset)), status_code


def _parse_v1_create(data: dict):
    """
    Parse v1 create request body.

    v1 format:
      {
        "amount": 19.99,        <- float dollars (BREAKING: v2 uses amount_cents int)
        "currency": "USD",
        "card_number": "4111111111111234",  <- full card; we store only last4
        "description": "..."    <- optional
      }
    """
    required = ("amount", "currency", "card_number")
    missing = [f for f in required if f not in data]
    if missing:
        return None, f"Missing fields: {', '.join(missing)}"

    try:
        amount_float = float(data["amount"])
    except (ValueError, TypeError):
        return None, "amount must be a number"

    card = str(data["card_number"])
    if len(card) < 4:
        return None, "card_number must be at least 4 digits"

    return {
        "amount_cents": int(round(amount_float * 100)),
        "currency": str(data["currency"]).upper(),
        "card_last4": card[-4:],
        "description": data.get("description"),
    }, None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@payment_v1_bp.route("", methods=["GET"])
def list_payments():
    """[v1] List all payments with offset pagination."""
    limit = min(int(request.args.get("limit", 10)), 100)
    offset = int(request.args.get("offset", 0))
    status_filter = request.args.get("status")

    query = Payment.query
    if status_filter:
        v1_to_v2 = {"success": "completed", "failed": "failed", "pending": "pending"}
        mapped = v1_to_v2.get(status_filter)
        if mapped:
            query = query.filter_by(status=mapped)

    total = query.count()
    payments = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()

    return _v1_response({
        "data": [p.to_v1() for p in payments],
        "pagination": {"total": total, "limit": limit, "offset": offset},
    })


@payment_v1_bp.route("/<int:payment_id>", methods=["GET"])
def get_payment(payment_id):
    """[v1] Get a single payment by ID."""
    payment = Payment.query.get_or_404(payment_id, description="Payment not found")
    return _v1_response(payment.to_v1())


@payment_v1_bp.route("", methods=["POST"])
def create_payment():
    """
    [v1] Create a payment.

    Request body (v1 format):
      {
        "amount": 19.99,
        "currency": "USD",
        "card_number": "4111111111111234"
      }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    parsed, error = _parse_v1_create(data)
    if error:
        return jsonify({"error": error}), 400

    payment = Payment(
        amount_cents=parsed["amount_cents"],
        currency=parsed["currency"],
        card_last4=parsed["card_last4"],
        description=parsed["description"],
        status="pending",
    )
    db.session.add(payment)
    db.session.commit()
    return _v1_response(payment.to_v1(), 201)


@payment_v1_bp.route("/<int:payment_id>/capture", methods=["POST"])
def capture_payment(payment_id):
    """[v1] Capture a pending payment (marks it as success)."""
    payment = Payment.query.get_or_404(payment_id, description="Payment not found")

    if payment.status != "pending":
        return jsonify({"error": "Only pending payments can be captured"}), 400

    payment.status = "completed"
    db.session.commit()
    return _v1_response(payment.to_v1())
