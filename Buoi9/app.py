from flask import Flask
from api.v1.payment_controller import api_v1
from api.v2.payment_controller import api_v2

app = Flask(__name__)

# Đăng ký blueprint
app.register_blueprint(api_v1, url_prefix='/api/v1')
app.register_blueprint(api_v2, url_prefix='/api/v2')

if __name__ == '__main__':
    print("Version 1: http://127.0.0.1:1604/api/v1/payments")
    print("Version 2: http://127.0.0.1:1604/api/v2/payments")
    app.run(debug=True, port=1604)