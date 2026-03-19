from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)

app.config ['SWAGGER'] = {
    'openapi': '3.0.0'
}
swagger = Swagger(app, template_file='openAPI.yaml')

books_db = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann"},
]

def send_response(success=True, data=None, message="", status_code=200):
    return jsonify({
        "success": success,
        "message": message,
        "data": data
    }), status_code

@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books"""
    return send_response(data=books_db, message="Books retrieved successfully")

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a book by its ID"""
    book = next((b for b in books_db if b['id'] == book_id), None)
    if book:
        return send_response(data=book, message="Book found")
    return send_response(success=False, message="Book not found", status_code=404)

@app.route('/api/books', methods=['POST'])
def add_book():
    """Add a new book"""
    if not request.json or not 'title' in request.json or not 'author' in request.json:
        return send_response(success=False, message="Missing title or author", status_code=400)
    
    new_book = {
        'id': books_db[-1]['id'] + 1 if books_db else 1,
        'title': request.json['title'],
        'author': request.json['author']
    }
    books_db.append(new_book)
    return send_response(data=new_book, message="Book created successfully", status_code=201)

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update an existing book"""
    book = next((b for b in books_db if b['id'] == book_id), None)
    if not book:
        return send_response(success=False, message="Book not found", status_code=404)
    
    if not request.json:
        return send_response(success=False, message="Invalid JSON", status_code=400)

    book['title'] = request.json.get('title', book['title'])
    book['author'] = request.json.get('author', book['author'])
    
    return send_response(data=book, message="Book updated successfully")

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    global books_db
    initial_len = len(books_db)
    books_db = [b for b in books_db if b['id'] != book_id]
    
    if len(books_db) == initial_len:
        return send_response(success=False, message="Book not found", status_code=404)
        
    return send_response(message="Book deleted successfully", status_code=204)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

