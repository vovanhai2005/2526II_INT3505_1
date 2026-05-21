from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/payment', methods=['POST'])
def payment_webhook():
    # Kiểm tra Content-Type phải là JSON
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.get_json()

    event   = data.get('event', 'unknown')
    payload = data.get('payload', {})

    print(f"\n[RECEIVER] Nhận được webhook sự kiện: {event}")
    print(f"[RECEIVER]   Order ID  : {payload.get('order_id')}")
    print(f"[RECEIVER]   Số tiền   : {payload.get('amount')} {payload.get('currency')}")
    print(f"[RECEIVER]   Trạng thái: {payload.get('status')}")

    # Xử lý theo loại sự kiện
    if event == "payment.success":
        print("[RECEIVER] => Xác nhận đơn hàng và gửi email cho khách hàng.")
    elif event == "payment.failed":
        print("[RECEIVER] => Thông báo thanh toán thất bại cho khách hàng.")
    else:
        print(f"[RECEIVER] => Sự kiện không xác định: {event}")

    return jsonify({"status": "success", "message": "Webhook received"}), 200


if __name__ == '__main__':
    print("Starting Payment Webhook Receiver on port 5001...")
    app.run(port=5001)
