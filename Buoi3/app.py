from flask import Flask, jsonify, request

app = Flask(__name__)

# -------------------------- Demo Naming Conventions --------------------------

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



# =============================
# Demo Clarity 
# =============================

# # WRONG case: 
# 1. Using POST to get data
# 2. URL include "get-book"
# 3. Passing ID as query parameter instead of path parameter.
# 4. Always returning 200 OK 


@app.route('/api/get-book', methods=['POST'])
def get_book_wrong():
    book_id = request.args.get('id')
    
    # Logic book search 
    
    return jsonify({
        "status": "error", 
        "message": "Không tìm thấy sách"
        }), 200

# CORRECT case:
# 1. Using GET to retrieve data.
# 2. URL contains plural noun "books"
# 3. Pass ID as path parameter.
# 4. Return 404 Not Found if book not found, otherwise return 200 OK with book data.

@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
def get_book_right(book_id):
    
    book_found = True
    
    if not book_found:
        return jsonify({"error": "Not Found"}), 404 
        
    return jsonify({
        "status": "success", 
        "data": {
            "id": book_id, 
            "title": "Clean Code"
            }
        }), 200

# ========================= 
# Demo Consistency 
# =========================

# WRONG case: 
# Inconsistent response formats across different endpoints.

# Endpoint 1 returns a direct array
@app.route('/api/v1/users-wrong', methods=['GET'])
def get_users_wrong():
    return jsonify([{
            "id": 1, 
            "name": "Nguyễn Văn A"
        }
    ]), 200

# Endpoint 2 returns an object with a specific resource key ("products")
@app.route('/api/v1/products-wrong', methods=['GET'])
def get_products_wrong():
    return jsonify({
        "products": [{
                "id": 101, 
                "name": "Laptop"
            }
        ]
    }), 200


# CORRECT case:
# 1. Consistent response envelope for all endpoints.
# 2. Both endpoints use the standard {"status": "success", "data": [...]} format.

@app.route('/api/v1/users', methods=['GET'])
def get_users_right():
    return jsonify({
        "status": "success",
        "data": [
            {"id": 1, "name": "Nguyễn Văn A"}
        ]
    }), 200

@app.route('/api/v1/products', methods=['GET'])
def get_products_right():
    return jsonify({
        "status": "success",
        "data": [
            {"id": 101, "name": "Laptop"}
        ]
    }), 200