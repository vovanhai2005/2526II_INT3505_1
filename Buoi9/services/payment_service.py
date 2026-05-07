import uuid
from datetime import datetime


def payment_response(status: str, message: str, **kwargs) -> dict:
    result = {
        "status": status,
        "message": message,
    }
    result.update(kwargs)
    return result


def process_payment(amount, currency: str):
    if not isinstance(amount, (int, float)) or amount <= 0:
        return payment_response(status="error", message="Số tiền không hợp lệ"), 400

    transaction_id = str(uuid.uuid4())
    return payment_response(
        status="success",
        message="Giao dịch thành công",
        transaction_id=transaction_id,
        amount=amount,
        currency=currency,
        timestamp=datetime.utcnow().isoformat() + "Z",
    ), 200
