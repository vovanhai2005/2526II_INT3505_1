from flask import Flask, request, jsonify

app = Flask(__name__)

users = {}
current_id = 1

# 1. Read all users
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values())), 200

# 2. Read one user
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({
            'error': 'User not found'
        }), 404

# 3. Create user
@app.route('/users', methods=['POST'])
def create_user():
    global current_id
    data = request.get_json(force=True)
    user = {'id': current_id, 'name': data.get('name'), 'email': data.get('email')}
    users[current_id] = user
    current_id += 1
    return jsonify(user), 201

# 4. Update user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if user_id in users:
        data = request.get_json(force=True)
        users[user_id].update({
            'name': data.get('name', users[user_id]['name']),
            'email': data.get('email', users[user_id]['email'])
        })
        return jsonify(users[user_id]), 200
    return jsonify({'error': 'User not found'}), 404

# 5. Delete user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id in users:
        del users[user_id]
        return '', 204
    return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(port=5002, debug=True)