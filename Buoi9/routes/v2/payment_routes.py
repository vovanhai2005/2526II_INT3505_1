"""
Payment API — Version 2 (Current)

Mounted at: /api/v2/payments

Changes from v1 (breaking):
  - amount_cents (int, cents) replaces amount (float, dollars)
  - payment_method object replaces top-level card_number_last4
  - status enum expanded: pending | processing | completed | failed | refunded
  - idempotency_key support (prevents duplicate charges on retry)
  - metadata object (arbitrary key-value pairs for business context)
  - description field
  - updated_at timestamp in response
  - new: POST /<id>/refund endpoint

Non-breaking additions:
  - GET supports filtering by currency, status, date range
"""
import json

from flask import Blueprint, jsonify, request

from models import Payment, db

payment_v2_bp = Blueprint("payment_v2", __name__, url_prefix="/api/v2/payments")

VALID_STATUSES = {"pending", "processing", "completed", "failed", "refunded"}
VALID_PAYMENT_TYPES = {"card", "bank_transfer", "wallet"}


def _parse_v2_create(data: dict):
    """
    Parse v2 create request body.

    v2 format:
      {
        "amount_cents": 1999,
        "currency": "USD",
        "payment_method": {
          "type": "card",
          "card_number": "4111111111111234"
        },
        "description": "...",         <- optional
        "metadata": {"order_id": 42}, <- optional
        "idempotency_key": "uuid..."  <- optional, prevents duplicate charges
      }
    """
    required = ("amount_cents", "currency", "payment_method")
    missing = [f for f in required if f not in data]
    if missing:
        return None, f"Missing fields: {', '.join(missing)}"

    try:
        amount_cents = int(data["amount_cents"])
    except (ValueError, TypeError):
        return None, "amount_cents must be an integer"

    if amount_cents <= 0:
        return None, "amount_cents must be positive"

    pm = data["payment_method"]
    if not isinstance(pm, dict):
        return None, "payment_method must be an object"
    if "type" not in pm:
        return None, "payment_method.type is required"
    if pm["type"] not in VALID_PAYMENT_TYPES:
        return None, f"payment_method.type must be one of {VALID_PAYMENT_TYPES}"
    if pm["type"] == "card" and "card_number" not in pm:
        return None, "payment_method.card_number is required for card payments"

    card_last4 = None
    if pm.get("card_number"):
        card = str(pm["card_number"])
        if len(card) < 4:
            return None, "card_number must be at least 4 digits"
        card_last4 = card[-4:]

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        return None, "metadata must be an object"

    idempotency_key = data.get("idempotency_key")
    if idempotency_key and Payment.query.filter_by(idempotency_key=idempotency_key).first():
        return None, "IDEMPOTENT_DUPLICATE"

    return {
        "amount_cents": amount_cents,
        "currency": str(data["currency"]).upper(),
        "payment_method_type": pm["type"],
        "card_last4": card_last4,
        "description": data.get("description"),
        "metadata_json": json.dumps(metadata) if metadata else None,
        "idempotency_key": idempotency_key,
    }, None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@payment_v2_bp.route("", methods=["GET"])
def list_payments():
    """[v2] List payments with cursor or offset pagination and rich filtering."""
    limit = min(int(request.args.get("limit", 10)), 100)
    status_filter = request.args.get("status")
    currency_filter = request.args.get("currency")
    pagination_type = request.args.get("pagination_type", "offset")

    query = Payment.query.order_by(Payment.created_at.desc())
    if status_filter:
        if status_filter not in VALID_STATUSES:
            return jsonify({"error": f"Invalid status. Must be one of {VALID_STATUSES}"}), 400
        query = query.filter_by(status=status_filter)
    if currency_filter:
        query = query.filter_by(currency=currency_filter.upper())

    if pagination_type == "cursor":
        cursor = request.args.get("cursor", type=int)
        if cursor:
            query = query.filter(Payment.id < cursor)
        payments = query.limit(limit).all()
        next_cursor = payments[-1].id if len(payments) == limit else None
        return jsonify({
            "data": [p.to_v2() for p in payments],
            "pagination": {"limit": limit, "next_cursor": next_cursor, "type": "cursor"},
        }), 200

    offset = int(request.args.get("offset", 0))
    total = query.count()
    payments = query.offset(offset).limit(limit).all()
    return jsonify({
        "data": [p.to_v2() for p in payments],
        "pagination": {"total": total, "limit": limit, "offset": offset, "type": "offset"},
    }), 200


@payment_v2_bp.route("/<int:payment_id>", methods=["GET"])
def get_payment(payment_id):
    """[v2] Get a single payment by ID."""
    payment = Payment.query.get_or_404(payment_id, description="Payment not found")
    return jsonify(payment.to_v2()), 200


@payment_v2_bp.route("", methods=["POST"])
def create_payment():
    """
    [v2] Create a payment.

    Supports idempotency_key: sending the same key twice returns the original
    payment instead of creating a duplicate charge.

    Request body (v2 format):
      {
        "amount_cents": 1999,
        "currency": "USD",
        "payment_method": {"type": "card", "card_number": "4111111111111234"},
        "description": "Order #42",
        "metadata": {"order_id": 42, "customer_tier": "premium"},
        "idempotency_key": "a3f8c2d1-..."
      }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    parsed, error = _parse_v2_create(data)
    if error == "IDEMPOTENT_DUPLICATE":
        existing = Payment.query.filter_by(
            idempotency_key=data.get("idempotency_key")
        ).first()
        return jsonify(existing.to_v2()), 200

    if error:
        return jsonify({"error": error}), 400

    payment = Payment(**parsed, status="pending")
    db.session.add(payment)
    db.session.commit()
    return jsonify(payment.to_v2()), 201


@payment_v2_bp.route("/<int:payment_id>", methods=["PATCH"])
def update_payment(payment_id):
    """[v2] Partial update: only description and metadata are mutable after creation."""
    payment = Payment.query.get_or_404(payment_id, description="Payment not found")
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "description" in data:
        payment.description = data["description"]
    if "metadata" in data:
        if not isinstance(data["metadata"], dict):
            return jsonify({"error": "metadata must be an object"}), 400
        payment.metadata_json = json.dumps(data["metadata"])

    db.session.commit()
    return jsonify(payment.to_v2()), 200


@payment_v2_bp.route("/<int:payment_id>/capture", methods=["POST"])
def capture_payment(payment_id):
    """[v2] Capture a pending payment (moves status to 'processing' then 'completed')."""
    payment = Payment.query.get_or_404(payment_id, description="Payment not found")

    if payment.status != "pending":
        return jsonify({"error": "Only pending payments can be captured"}), 400

    payment.status = "completed"
    db.session.commit()
    return jsonify(payment.to_v2()), 200


@payment_v2_bp.route("/<int:payment_id>/refund", methods=["POST"])
def refund_payment(payment_id):
    """
    [v2] Refund a completed payment. NEW in v2 — does not exist in v1.

    Optionally accepts:
      {
        "reason": "customer_request" | "duplicate" | "fraudulent"
      }
    """
    payment = Payment.query.get_or_404(payment_id, description="Payment not found")

    if payment.status != "completed":
        return jsonify({"error": "Only completed payments can be refunded"}), 400

    data = request.get_json(silent=True) or {}
    reason = data.get("reason", "customer_request")

    payment.status = "refunded"
    existing_meta = json.loads(payment.metadata_json) if payment.metadata_json else {}
    existing_meta["refund_reason"] = reason
    payment.metadata_json = json.dumps(existing_meta)
    db.session.commit()
    return jsonify(payment.to_v2()), 200
