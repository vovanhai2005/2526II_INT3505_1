from flask import Blueprint, request, jsonify
from services.payment_service import process_payment, payment_response

api_v2 = Blueprint('api_v2', __name__)

@api_v2.route('/payments', methods=['POST'])
def create_payment_v2():
    """
    Tạo giao dịch thanh toán đa tiền tệ
    """
    data = request.get_json()
    
    if not data or 'amount' not in data or 'currency' not in data:
        error_response = payment_response(
            status="error", 
            message="Thiếu dữ liệu!"
        )
        return jsonify(error_response), 400

    amount = data['amount']
    currency = str(data['currency']).upper()
    
    allowed_currencies = ["VND", "USD", "EUR", "JPY"]
    if currency not in allowed_currencies:
        error_response = payment_response(
            status="error", 
            message=f"{currency} chưa được hỗ trợ!"
        )
        return jsonify(error_response), 400
        
    result_dict, status_code = process_payment(amount, currency)

    return jsonify(result_dict), status_code