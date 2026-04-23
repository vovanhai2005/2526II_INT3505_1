"""
Alternative versioning strategies demo.

This module exposes a single Blueprint at /api/payments that demonstrates
two additional versioning strategies beyond URL-based versioning:

  Strategy 2 — Header versioning
    Request header:  API-Version: v1   or   API-Version: v2
    Accept header:   application/vnd.payment.v1+json

  Strategy 3 — Query parameter versioning
    Query string:    /api/payments?version=v1   or   /api/payments?version=v2

Both strategies share the same business logic as the dedicated URL blueprints;
they simply resolve the version at request time and delegate accordingly.

Comparison of strategies
--------------------------
| Strategy    | Example                        | Pros                        | Cons                          |
|-------------|--------------------------------|-----------------------------|-------------------------------|
| URL         | /api/v1/payments               | Obvious, cache-friendly     | URL changes on every version  |
| Header      | API-Version: v2                | Clean URL, REST-ish         | Harder to test in a browser   |
| Query param | /api/payments?version=v2       | Easy to test, no config     | Pollutes query string         |
"""
import json

from flask import Blueprint, current_app, jsonify, request

from middleware.deprecation import inject_deprecation_warning
from models import Payment, db
from routes.v1.payment_routes import _parse_v1_create
from routes.v2.payment_routes import _parse_v2_create, VALID_STATUSES

dispatcher_bp = Blueprint("dispatcher", __name__, url_prefix="/api/payments")

# ---------------------------------------------------------------------------
# Version resolution helpers
# ---------------------------------------------------------------------------

def _resolve_version() -> str:
    """
    Determine API version from the request using the following priority:
      1. X-API-Version header
      2. Accept header (application/vnd.payment.vN+json)
      3. version query parameter
      4. Default to v2
    """
    header_version = request.headers.get("API-Version") or request.headers.get("X-API-Version")
    if header_version in ("v1", "v2", "1", "2"):
        return "v1" if header_version in ("v1", "1") else "v2"

    accept = request.headers.get("Accept", "")
    if "vnd.payment.v1" in accept:
        return "v1"
    if "vnd.payment.v2" in accept:
        return "v2"

    query_version = request.args.get("version", "")
    if query_version in ("v1", "1"):
        return "v1"
    if query_version in ("v2", "2"):
        return "v2"

    return "v2"


def _wrap(data: dict, version: str, status_code: int = 200):
    sunset = current_app.config.get("API_V1_SUNSET_DATE", "2026-12-31")
    if version == "v1":
        data = inject_deprecation_warning(data, sunset)
    return jsonify(data), status_code


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@dispatcher_bp.route("", methods=["GET"])
def list_payments():
    """
    [dispatcher] List payments — version resolved from header or query param.

    Header strategy:  curl -H "API-Version: v1" /api/payments
    Query strategy:   curl /api/payments?version=v1
    """
    version = _resolve_version()
    limit = min(int(request.args.get("limit", 10)), 100)
    offset = int(request.args.get("offset", 0))

    query = Payment.query.order_by(Payment.created_at.desc())
    total = query.count()
    payments = query.offset(offset).limit(limit).all()

    serializer = Payment.to_v1 if version == "v1" else Payment.to_v2
    data = {
        "data": [serializer(p) for p in payments],
        "pagination": {"total": total, "limit": limit, "offset": offset},
        "_version_resolved": version,
        "_resolution_strategy": _describe_resolution(),
    }
    return _wrap(data, version)


@dispatcher_bp.route("/<int:payment_id>", methods=["GET"])
def get_payment(payment_id):
    """[dispatcher] Get a single payment — version resolved from header or query param."""
    version = _resolve_version()
    payment = Payment.query.get_or_404(payment_id, description="Payment not found")
    serializer = payment.to_v1 if version == "v1" else payment.to_v2
    data = {**serializer(), "_version_resolved": version}
    return _wrap(data, version)


@dispatcher_bp.route("", methods=["POST"])
def create_payment():
    """[dispatcher] Create a payment — version resolved from header or query param."""
    version = _resolve_version()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    if version == "v1":
        parsed, error = _parse_v1_create(data)
        if error:
            return jsonify({"error": error}), 400
        payment = Payment(**parsed, status="pending")
    else:
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

    serializer = payment.to_v1 if version == "v1" else payment.to_v2
    body = {**serializer(), "_version_resolved": version}
    return _wrap(body, version, 201)


@dispatcher_bp.route("/strategies", methods=["GET"])
def versioning_strategies():
    """
    [dispatcher] Explain all supported versioning strategies and how to use them.

    This is a meta-endpoint for developer education — not part of the business API.
    """
    return jsonify({
        "supported_strategies": [
            {
                "name": "URL versioning",
                "description": "Version is embedded in the URL path.",
                "examples": {
                    "v1": "GET /api/v1/payments",
                    "v2": "GET /api/v2/payments",
                },
                "pros": ["Obvious and explicit", "Easy to bookmark/share", "Cache-friendly"],
                "cons": ["URL changes on every version bump", "Can feel non-REST-ish"],
                "recommendation": "Best for public APIs with long support windows.",
            },
            {
                "name": "Header versioning",
                "description": "Version is specified via the API-Version or Accept header.",
                "examples": {
                    "v1_header": "GET /api/payments  [API-Version: v1]",
                    "v2_header": "GET /api/payments  [API-Version: v2]",
                    "v1_accept": "GET /api/payments  [Accept: application/vnd.payment.v1+json]",
                },
                "pros": ["Clean, stable URLs", "Follows HTTP content negotiation spec"],
                "cons": ["Harder to test in a browser", "Requires explicit client configuration"],
                "recommendation": "Best for internal APIs or SDKs where the client controls headers.",
            },
            {
                "name": "Query parameter versioning",
                "description": "Version is specified as a query string parameter.",
                "examples": {
                    "v1": "GET /api/payments?version=v1",
                    "v2": "GET /api/payments?version=v2",
                },
                "pros": ["Easy to test in a browser", "No special tooling needed"],
                "cons": ["Pollutes query strings", "Often forgotten in filters/pagination"],
                "recommendation": "Good for prototyping or developer portals.",
            },
        ],
        "resolution_priority": [
            "1. API-Version / X-API-Version header",
            "2. Accept: application/vnd.payment.vN+json header",
            "3. ?version= query parameter",
            "4. Default: v2",
        ],
    }), 200


def _describe_resolution() -> str:
    """Return a human-readable description of how the version was resolved."""
    if request.headers.get("API-Version") or request.headers.get("X-API-Version"):
        return "header (API-Version)"
    accept = request.headers.get("Accept", "")
    if "vnd.payment.v" in accept:
        return "header (Accept)"
    if request.args.get("version"):
        return "query_param (?version)"
    return "default (v2)"
