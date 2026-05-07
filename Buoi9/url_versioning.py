from flask import Flask, Blueprint, jsonify

app = Flask(__name__)
v1 = Blueprint('v1', __name__, url_prefix='/api/v1')
v2 = Blueprint('v2', __name__, url_prefix='/api/v2')

@v1.route('/users')
def get_users_v1():
    return jsonify({
        "users": [
            "Alice", 
            "Bob"
                ]
        })

@v2.route('/users')
def get_users_v2():
    return jsonify({
        "data": [
            {"name": "Alice"}, 
            {"name": "Bob"},
            {"name": "Charlie"}
            ]
        })

app.register_blueprint(v1)
app.register_blueprint(v2)

if __name__ == "__main__":
    app.run(debug=True)