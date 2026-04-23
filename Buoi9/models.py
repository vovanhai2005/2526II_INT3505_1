import json
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    # Canonical v2 storage: amount in smallest currency unit (cents)
    amount_cents = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="USD")
    payment_method_type = db.Column(db.String(20), nullable=False, default="card")
    card_last4 = db.Column(db.String(4), nullable=True)
    # v2 status enum: pending | processing | completed | failed | refunded
    status = db.Column(db.String(20), nullable=False, default="pending")
    metadata_json = db.Column(db.Text, nullable=True)
    idempotency_key = db.Column(db.String(64), nullable=True, unique=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_v1(self):
        """
        Serialize to v1 format.

        Breaking differences from v2:
          - amount is float (dollars), not integer cents
          - card exposed as top-level `card_number_last4` instead of nested payment_method
          - status simplified: "success" | "failed" | "pending" (no processing/refunded)
          - no metadata, idempotency_key, description, updated_at
        """
        v1_status_map = {
            "completed": "success",
            "failed": "failed",
            "refunded": "failed",
        }
        return {
            "id": self.id,
            "amount": self.amount_cents / 100.0,
            "currency": self.currency,
            "card_number_last4": self.card_last4,
            "status": v1_status_map.get(self.status, "pending"),
            "created_at": self.created_at.isoformat(),
        }

    def to_v2(self):
        """Serialize to v2 format."""
        metadata = json.loads(self.metadata_json) if self.metadata_json else {}
        return {
            "id": self.id,
            "amount_cents": self.amount_cents,
            "currency": self.currency,
            "payment_method": {
                "type": self.payment_method_type,
                "last4": self.card_last4,
            },
            "status": self.status,
            "metadata": metadata,
            "description": self.description,
            "idempotency_key": self.idempotency_key,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
