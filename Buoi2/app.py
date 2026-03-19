import time
import jwt
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key'  # Change this in a real app!

# Demo Client-Server Constraint

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the REST API!"}), 200

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
    {"id": 2, "title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann"},
    {"id": 3, "title": "The Pragmatic Programmer", "author": "Andrew Hunt and David Thomas"}
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

# Demo Stateless Constraint with JWT

USERS = {
    "admin": "123456",
    "guest": "guestpass"
}

@app.route('/api/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if auth.username in USERS and USERS[auth.username] == auth.password:
        token = jwt.encode({
            'user': auth.username,
            'role': 'admin' if auth.username == 'admin' else 'guest',
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/api/my-profile', methods=['GET'])
def get_profile():
    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]

    if not token:
        return jsonify({"error": "Unauthorized. Token is missing."}), 401

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user_name = data['user']
        role = data['role']
        return jsonify({
            "message": f"Hello {user_name}!",
            "role": role
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token."}), 401

# --- Demo Cacheable Constraint ---

@app.route('/api/config', methods=['GET'])
def get_config():
    data = {
        "theme": "dark",
        "version": "1.0.0",
        "server_time": time.time()
    }
    
    response = make_response(jsonify(data))
    response.headers['Cache-Control'] = 'public, max-age=30'
    
    return response, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)