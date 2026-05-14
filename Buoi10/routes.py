# pyrefly: ignore [missing-import]
from flask import Blueprint, jsonify, current_app
from extensions import limiter

api_bp = Blueprint('api', __name__)

# Endpoint 1: Public - dùng default limit (50 req/giờ)
@api_bp.route("/public")
def public_api():
    current_app.logger.info("Một người dùng vừa truy cập API public.")
    return jsonify({"message": "API này giới hạn 50 request/giờ theo mặc định."})

# Endpoint 2: Sensitive - giới hạn chặt hơn (3 req/phút)
@api_bp.route("/sensitive")
@limiter.limit("3 per minute")
def sensitive_api():
    current_app.logger.warning("Truy cập vào API nhạy cảm!")
    return jsonify({"message": "API này chỉ cho phép 3 request/phút."})

# Endpoint 3: Cố tình gây lỗi để test error logging
@api_bp.route("/error")
def trigger_error():
    current_app.logger.info("Đang cố gắng thực hiện một phép tính nguy hiểm...")
    # pyrefly: ignore [division-by-zero]
    1 / 0
    # pyrefly: ignore [unreachable]
    return jsonify({"message": "Sẽ không bao giờ chạy đến dòng này"})