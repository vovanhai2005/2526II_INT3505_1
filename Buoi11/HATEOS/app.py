from typing import Any
from flask import Flask, jsonify, request

app = Flask(__name__)

# Giả lập Database với các trạng thái khác nhau - Cửa hàng sách
orders = {
    1: {"id": 1, "title": "Clean Code",             "genre": "technology",  "author": "Robert C. Martin", "price": 35.99, "status": "pending"},
    2: {"id": 2, "title": "The Pragmatic Programmer","genre": "technology",  "author": "David Thomas",      "price": 42.50, "status": "paid"},
    3: {"id": 3, "title": "Dune",                    "genre": "sci-fi",      "author": "Frank Herbert",     "price": 18.00, "status": "shipped"},
    4: {"id": 4, "title": "Foundation",              "genre": "sci-fi",      "author": "Isaac Asimov",      "price": 15.75, "status": "pending"},
    5: {"id": 5, "title": "Sapiens",                 "genre": "non-fiction", "author": "Yuval Noah Harari", "price": 22.00, "status": "paid"},
    6: {"id": 6, "title": "Atomic Habits",           "genre": "non-fiction", "author": "James Clear",       "price": 19.99, "status": "shipped"},
    7: {"id": 7, "title": "The Hobbit",              "genre": "fantasy",     "author": "J.R.R. Tolkien",    "price": 14.50, "status": "pending"},
    8: {"id": 8, "title": "1984",                    "genre": "sci-fi",      "author": "George Orwell",     "price": 12.99, "status": "cancelled"},
}

def generate_links(order_id, status):
    """
    Tạo mảng links (HATEOAS) phụ thuộc vào trạng thái (state) hiện tại của đối tượng.
    """
    base_url = f"http://localhost:5004/orders/{order_id}"
    links = [
        {"rel": "self", "href": base_url, "method": "GET"}  # Luôn có link tham chiếu đến chính nó
    ]

    # State Machine: Nếu pending -> Có thể pay (thanh toán) hoặc cancel (hủy)
    if status == "pending":
        links.append({"rel": "pay",    "href": f"{base_url}/pay",    "method": "POST"})
        links.append({"rel": "cancel", "href": f"{base_url}/cancel", "method": "POST"})

    # State Machine: Nếu paid -> Có thể ship (giao hàng) hoặc refund (hoàn tiền)
    elif status == "paid":
        links.append({"rel": "ship",   "href": f"{base_url}/ship",   "method": "POST"})
        links.append({"rel": "refund", "href": f"{base_url}/refund", "method": "POST"})

    return links

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    response: dict[str, Any] = order.copy()
    # Nhúng thông tin HATEOAS vào response
    response["_links"] = generate_links(order_id, order["status"])
    return jsonify(response), 200

@app.route('/orders/<int:order_id>/pay', methods=['POST'])
def pay_order(order_id):
    order = orders.get(order_id)
    if order and order["status"] == "pending":
        order["status"] = "paid"
        return get_order(order_id)  # Trả về state mới kèm các link mới (ship, refund)
    return jsonify({"error": "Cannot pay this order. Invalid state."}), 400

if __name__ == '__main__':
    print("Starting HATEOAS API on port 5004...")
    app.run(port=5004)
