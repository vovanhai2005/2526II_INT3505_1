from flask import Flask, request, jsonify
import threading
import queue
import time

app = Flask(__name__)

# Một message broker đơn giản dùng trong RAM thay cho Kafka/RabbitMQ
event_queue = queue.Queue()

def event_worker():
    """
    Hàm này chạy trên một Background Thread riêng biệt đóng vai trò là (Consumer/Subscriber)
    """
    print("[CONSUMER] Event processor started in background...")
    while True:
        # Lấy sự kiện ra từ hàng đợi
        event = event_queue.get()
        if event is None:
            break
            
        print(f"\n[CONSUMER] Nhận được sự kiện: {event['name']} (ID: {event['id']})")
        print(f"[CONSUMER] Đang xử lý tốn nhiều thời gian...")
        
        # Giả lập công việc tốn thời gian (ví dụ: encode video, gọi API thứ 3 gửi email, ...)
        time.sleep(3) 
        
        print(f"[CONSUMER] => Đã xử lý xong sự kiện ID: {event['id']}\n")
        event_queue.task_done()

# Khởi động Background Consumer Thread
worker_thread = threading.Thread(target=event_worker, daemon=True)
worker_thread.start()

event_counter = 1

@app.route('/upload_video', methods=['POST'])
def upload_video():
    """
    Endpoint (Producer/Publisher) nhận yêu cầu từ User.
    Thay vì bắt user chờ 3s mới trả về response, nó sẽ phát (Publish) sự kiện vào Queue.
    """
    global event_counter
    video_data = request.get_json(silent=True)
    if not video_data:
        return jsonify({"error": "Request body must be valid JSON."}), 400
    
    event = {
        "id": event_counter,
        "name": "video.uploaded",
        "payload": video_data.get("filename", "unknown_file.mp4")
    }
    
    # 1. Đưa sự kiện vào Hàng đợi (Push Event)
    event_queue.put(event)
    event_counter += 1
    
    # 2. Rất nhanh, trả về phản hồi cho user ngay lập tức mà không phải chờ xử lý xong
    # HTTP 202 Accepted: Đã ghi nhận nhưng chưa xử lý xong
    return jsonify({
        "status": "success",
        "message": "Video đã được thêm vào hàng đợi để xử lý đồ họa.",
        "job_id": event["id"]
    }), 202 

if __name__ == '__main__':
    print("Starting Event-Driven API on port 5005...")
    app.run(port=5005)