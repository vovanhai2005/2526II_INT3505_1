# demo query parameter versioning
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/users')
def get_users():
    version = request.args.get('v', '1')
    if version == '2':
        return jsonify({"data": [{"name": "Alice"}, {"name": "Bob"}]})
    return jsonify({"users": ["Alice", "Bob", "Charlie"]})

if __name__ == "__main__":
    app.run(debug=True)