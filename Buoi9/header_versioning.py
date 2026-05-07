# demo Header Versioning
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/users')
def get_users():
    version = request.headers.get('X-API-Version', '1.0')
    if version == '2.0':
        return jsonify({"data": [{"name": "Alice"}]})
    return jsonify({"users": ["Alice", "Bob", "Charlie"]})

if __name__ == "__main__":
    app.run(debug=True)