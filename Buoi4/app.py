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

if __name__ == '__main__':
    app.run(debug=True, port=5000)

