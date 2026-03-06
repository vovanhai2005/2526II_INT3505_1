from flask import Flask, jsonify, request

app = Flask(__name__)

# Demo Client-Server Constraint

@app.route('/api/system-info', methods=['GET'])
def get_system_info():
    data = {
        "server_engine": "Flask",
        "status": "Operational",
        "message": "Dữ liệu này độc lập với giao diện người dùng."
    }
    return jsonify(data), 200

# Demo Uniform Interface Constraint

books_db = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann"}
]

@app.route('/api/books', methods=['GET'])
def get_books():
    return jsonify(books_db), 200

@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.get_json()
    new_book = {
        "id": len(books_db) + 1,
        "title": data.get("title"),
        "author": data.get("author")
    }
    books_db.append(new_book)
    return jsonify(new_book), 201 

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books_db
    books_db = [b for b in books_db if b['id'] != book_id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=5000)