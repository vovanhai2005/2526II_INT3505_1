import logging
from logging.handlers import RotatingFileHandler
# pyrefly: ignore [missing-import]
from flask import Flask, jsonify, request
from extensions import limiter
from routes import api_bp
# pyrefly: ignore [missing-import]
from prometheus_flask_exporter import PrometheusMetrics

def create_app():
    app = Flask(__name__)

    metrics = PrometheusMetrics(app)

    # 1. Gắn Limiter vào app
    limiter.init_app(app)

    # 2. Đăng ký Blueprint với prefix /api
    app.register_blueprint(api_bp, url_prefix='/api')

    # 3. Thiết lập Logging
    setup_logging(app)

    # 4. Xử lý lỗi tập trung
    register_error_handlers(app)

    return app


def setup_logging(app):
    # Ghi log ra file, tối đa 5MB, giữ 3 bản backup
    file_handler = RotatingFileHandler(
        'app_production.log',
        maxBytes=5_000_000,
        backupCount=3,
        encoding='utf-8'
    )

    # Định dạng dòng log
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)

    # Gắn handler vào logger của Flask
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # Tự động log TRƯỚC mỗi request
    @app.before_request
    def log_request_info():
        app.logger.info(
            f"Yêu cầu đến: {request.method} {request.url} | IP: {request.remote_addr}"
        )

    # Tự động log SAU mỗi request
    @app.after_request
    def log_response_info(response):
        app.logger.info(f"Phản hồi: {response.status_code}")
        return response


def register_error_handlers(app):
    # Xử lý lỗi 429 - Rate Limit
    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(
            f"Người dùng bị chặn do Rate Limit: {request.remote_addr}"
        )
        return jsonify({
            "error": f"Bạn đã gửi quá nhiều yêu cầu: {e.description}"
        }), 429

    # Xử lý lỗi 500 - Lỗi hệ thống
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(
            f"Lỗi hệ thống không mong muốn: {str(e)}", exc_info=True
        )
        return jsonify({"error": "Đã xảy ra lỗi hệ thống (500)."}), 500


# Khởi tạo và chạy app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)