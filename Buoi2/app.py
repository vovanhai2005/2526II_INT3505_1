from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/system-info', methods=['GET'])
def get_system_info():
    data = {
        "server_engine": "Flask",
        "status": "Operational",
        "message": "Dữ liệu này độc lập với giao diện người dùng."
    }
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)