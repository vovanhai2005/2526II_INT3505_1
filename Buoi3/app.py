from flask import Flask, jsonify, request

app = Flask(__name__)

# Demo Naming Conventions

# - Versioning: /api/v1/
# - Plural noun & Lowercase: /payment-methods
# - Hyphens: Using - instead of _
@app.route('/api/v1/payment-methods', methods=['GET'])
def get_payment_methods():
    return jsonify({"status": "success", "data": []}), 200

# No versioning, use camelCase and include get in the name
@app.route('/getPaymentMethods', methods=['GET'])
def bad_naming():
    return jsonify([]), 200



# Demo Clarity
# LỖI: 
# 1. Dùng POST để lấy dữ liệu (Nên dùng GET).
# 2. URL chứa động từ "get-book".
# 3. Truyền ID qua query string thay vì path variable cho 1 tài nguyên cụ thể.
# 4. Luôn trả về 200 OK dù có tìm thấy sách hay không.


@app.route('/api/get-book', methods=['POST'])
def get_book_wrong():
    book_id = request.args.get('id')
    
    # Logic book search 
    
    return jsonify({"status": "error", "message": "Không tìm thấy sách"}), 200

# CHUẨN:
# 1. Dùng GET đúng ngữ nghĩa đọc dữ liệu.
# 2. URL là danh từ số nhiều (/books).
# 3. Truyền ID trực tiếp vào URL để định danh tài nguyên (/books/1).
# 4. Trả về đúng HTTP Status Code: 200 nếu thấy, 404 nếu không thấy.
@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
def get_book_right(book_id):
    
    # ... logic tìm sách ...
    book_found = True # Giả lập kết quả
    
    if not book_found:
        # 404 Not Found: Rõ ràng ngay từ HTTP Status
        return jsonify({"error": "Not Found"}), 404 
        
    # 200 OK: Lấy dữ liệu thành công
    return jsonify({"status": "success", "data": {"id": book_id, "title": "Clean Code"}}), 200
