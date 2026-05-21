import requests

# URL của Webhook Receiver đang chạy
WEBHOOK_URL = "http://localhost:5001/webhook/payment"

def send_webhook(event: str, payload: dict):
    """Gửi một webhook event đến receiver."""
    body = {
        "event":   event,
        "payload": payload
    }

    print(f"\n[SENDER] Đang gửi webhook: {event}")
    response = requests.post(WEBHOOK_URL, json=body)
    print(f"[SENDER] Phản hồi từ receiver: {response.status_code} — {response.json()}")


if __name__ == '__main__':
    # Giả lập thanh toán thành công
    send_webhook("payment.success", {
        "order_id": "ORD-1001",
        "amount":   250.00,
        "currency": "USD",
        "status":   "paid"
    })

    # Giả lập thanh toán thất bại
    send_webhook("payment.failed", {
        "order_id": "ORD-1002",
        "amount":   75.50,
        "currency": "USD",
        "status":   "failed"
    })
