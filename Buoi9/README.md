# Buổi 9: API Versioning và Lifecycle Management

Demo project: **Payment API** với đầy đủ 3 chiến lược versioning, migration plan v1→v2, và deprecation notice theo chuẩn RFC.

---

## Mục lục

1. [Kiến trúc tổng quan](#1-kiến-trúc-tổng-quan)
2. [Cài đặt và chạy](#2-cài-đặt-và-chạy)
3. [Chiến lược 1: URL Versioning](#3-chiến-lược-1-url-versioning)
4. [Chiến lược 2: Header Versioning](#4-chiến-lược-2-header-versioning)
5. [Chiến lược 3: Query Parameter Versioning](#5-chiến-lược-3-query-parameter-versioning)
6. [Case Study: Migration Plan v1 → v2](#6-case-study-migration-plan-v1--v2)
7. [Deprecation Notice cho Developers](#7-deprecation-notice-cho-developers)
8. [So sánh các chiến lược](#8-so-sánh-các-chiến-lược)

---

## 1. Kiến trúc tổng quan

```
Buoi9/
├── app.py                          # Flask app entry point
├── config.py                       # Cấu hình (DB, sunset date)
├── models.py                       # SQLAlchemy model (Payment)
│
├── middleware/
│   └── deprecation.py              # RFC 8594 deprecation headers + body warning
│
├── routes/
│   ├── v1/
│   │   └── payment_routes.py       # /api/v1/payments  (DEPRECATED)
│   └── v2/
│       └── payment_routes.py       # /api/v2/payments  (current)
│
└── versioning/
    └── dispatcher.py               # /api/payments  (header + query param demo)
```

### Tất cả endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/v1/payments` | [v1] Danh sách payment *(deprecated)* |
| POST | `/api/v1/payments` | [v1] Tạo payment *(deprecated)* |
| GET | `/api/v1/payments/<id>` | [v1] Lấy payment theo ID *(deprecated)* |
| POST | `/api/v1/payments/<id>/capture` | [v1] Capture payment *(deprecated)* |
| GET | `/api/v2/payments` | [v2] Danh sách payment |
| POST | `/api/v2/payments` | [v2] Tạo payment |
| GET | `/api/v2/payments/<id>` | [v2] Lấy payment theo ID |
| PATCH | `/api/v2/payments/<id>` | [v2] Cập nhật metadata/description |
| POST | `/api/v2/payments/<id>/capture` | [v2] Capture payment |
| POST | `/api/v2/payments/<id>/refund` | [v2] Hoàn tiền *(mới trong v2)* |
| GET/POST | `/api/payments` | [dispatcher] Header hoặc query param versioning |
| GET | `/api/payments/strategies` | [meta] Giải thích 3 chiến lược versioning |

---

## 2. Cài đặt và chạy

```bash
# Clone/cd vào thư mục
cd Buoi9

# Kích hoạt virtualenv (dùng chung với cả project)
source ../venv/bin/activate

# Cài dependencies (nếu chưa có)
pip install flask flask-sqlalchemy

# Chạy server
python app.py
# Server khởi động tại http://localhost:8080
```

---

## 3. Chiến lược 1: URL Versioning

> **Phiên bản được embed thẳng vào URL path.**

Đây là chiến lược phổ biến nhất và rõ ràng nhất.

### Tạo payment — v1 (legacy)

```bash
curl -X POST http://localhost:8080/api/v1/payments \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 19.99,
    "currency": "USD",
    "card_number": "4111111111111234",
    "description": "Order #100"
  }'
```

**Response v1:**
```json
{
  "id": 1,
  "amount": 19.99,
  "currency": "USD",
  "card_number_last4": "1234",
  "status": "pending",
  "created_at": "2026-04-23T12:00:00",
  "_deprecation_warning": {
    "message": "This API version (v1) is deprecated...",
    "sunset_date": "2026-12-31",
    "successor": "/api/v2/payments"
  }
}
```

### Tạo payment — v2 (current)

```bash
curl -X POST http://localhost:8080/api/v2/payments \
  -H "Content-Type: application/json" \
  -d '{
    "amount_cents": 4999,
    "currency": "USD",
    "payment_method": {
      "type": "card",
      "card_number": "4111111111115678"
    },
    "description": "Order #101",
    "metadata": { "order_id": 42, "customer_tier": "premium" },
    "idempotency_key": "order-42-attempt-1"
  }'
```

**Response v2:**
```json
{
  "id": 2,
  "amount_cents": 4999,
  "currency": "USD",
  "payment_method": { "type": "card", "last4": "5678" },
  "status": "pending",
  "metadata": { "order_id": 42, "customer_tier": "premium" },
  "description": "Order #101",
  "idempotency_key": "order-42-attempt-1",
  "created_at": "2026-04-23T12:00:00",
  "updated_at": "2026-04-23T12:00:00"
}
```

### Capture và Refund

```bash
# Capture payment (v2)
curl -X POST http://localhost:8080/api/v2/payments/2/capture

# Refund payment — CHỈ có trong v2, không có trong v1
curl -X POST http://localhost:8080/api/v2/payments/2/refund \
  -H "Content-Type: application/json" \
  -d '{"reason": "customer_request"}'
```

---

## 4. Chiến lược 2: Header Versioning

> **Client chỉ định version qua HTTP header `API-Version`.**
> URL không thay đổi — phù hợp với HTTP content negotiation.

```bash
# Dùng API-Version header để chọn v1
curl http://localhost:8080/api/payments \
  -H "API-Version: v1"

# Dùng API-Version header để chọn v2
curl http://localhost:8080/api/payments \
  -H "API-Version: v2"

# Dùng Accept header theo chuẩn vendor MIME type
curl http://localhost:8080/api/payments \
  -H "Accept: application/vnd.payment.v2+json"
```

**Response kèm thông tin version resolution:**
```json
{
  "_version_resolved": "v1",
  "_resolution_strategy": "header (API-Version)",
  "data": [...],
  "pagination": {...}
}
```

---

## 5. Chiến lược 3: Query Parameter Versioning

> **Version được truyền qua query string `?version=v1|v2`.**
> Dễ test trực tiếp trên browser, không cần tool.

```bash
# Query param → v1
curl "http://localhost:8080/api/payments?version=v1"

# Query param → v2
curl "http://localhost:8080/api/payments?version=v2"

# Không truyền → mặc định v2
curl "http://localhost:8080/api/payments"
```

### Xem giải thích đầy đủ 3 chiến lược

```bash
curl http://localhost:8080/api/payments/strategies
```

---

## 6. Case Study: Migration Plan v1 → v2

### Tại sao cần v2? — Breaking Changes

| Field / Feature | v1 (deprecated) | v2 (current) | Loại thay đổi |
|-----------------|-----------------|--------------|---------------|
| Số tiền | `"amount": 19.99` (float, dollars) | `"amount_cents": 1999` (integer, cents) | **Breaking** |
| Thông tin thẻ | `"card_number_last4": "1234"` | `"payment_method": {"type": "card", "last4": "1234"}` | **Breaking** |
| Status values | `"pending"`, `"success"`, `"failed"` | `"pending"`, `"processing"`, `"completed"`, `"failed"`, `"refunded"` | **Breaking** |
| Idempotency | Không có | `"idempotency_key"` | Non-breaking (addition) |
| Metadata | Không có | `"metadata": {}` | Non-breaking (addition) |
| Refund endpoint | Không có | `POST /payments/<id>/refund` | Non-breaking (addition) |
| Timestamps | `created_at` | `created_at` + `updated_at` | Non-breaking (addition) |

### Lý do thay đổi `amount` từ float → cents

```
# Vấn đề với float:
0.1 + 0.2 = 0.30000000000000004  ← lỗi rounding trong tài chính!

# Giải pháp: dùng integer cents
199 cents = $1.99  ← chính xác tuyệt đối
```

### Migration Guide cho Client (v1 → v2)

**Bước 1 — Cập nhật request body**

```python
# TRƯỚC (v1)
payload = {
    "amount": 19.99,
    "currency": "USD",
    "card_number": "4111111111111234"
}

# SAU (v2)
payload = {
    "amount_cents": 1999,           # float → int cents
    "currency": "USD",
    "payment_method": {             # card_number → nested object
        "type": "card",
        "card_number": "4111111111111234"
    },
    "idempotency_key": "unique-id"  # thêm để tránh double charge
}
```

**Bước 2 — Cập nhật parsing response**

```python
# TRƯỚC (v1)
amount_display = response["amount"]                    # 19.99
card = response["card_number_last4"]                   # "1234"
is_paid = response["status"] == "success"

# SAU (v2)
amount_display = response["amount_cents"] / 100        # 1999 → 19.99
card = response["payment_method"]["last4"]             # "1234"
is_paid = response["status"] == "completed"            # "success" → "completed"
```

**Bước 3 — Xử lý status mới**

```python
# v2 có thêm "processing" và "refunded"
STATUS_MAP = {
    "pending":    "Chờ xử lý",
    "processing": "Đang xử lý",    # MỚI trong v2
    "completed":  "Thành công",
    "failed":     "Thất bại",
    "refunded":   "Đã hoàn tiền",  # MỚI trong v2
}
```

**Bước 4 — Cập nhật URL**

```
GET  /api/v1/payments     →  GET  /api/v2/payments
POST /api/v1/payments     →  POST /api/v2/payments
POST /api/v1/payments/capture  →  POST /api/v2/payments/capture
(không có)                →  POST /api/v2/payments/refund  (mới)
```

### Lịch trình migration

| Mốc thời gian | Hành động |
|---------------|-----------|
| 2026-04-23 | v2 ra mắt, v1 bắt đầu nhận deprecation headers |
| 2026-06-01 | Email thông báo gửi tới tất cả developers đang dùng v1 |
| 2026-09-01 | v1 rate limit giảm xuống 20% so với v2 |
| 2026-12-31 | **Sunset date** — v1 bị tắt, trả về HTTP 410 Gone |

---

## 7. Deprecation Notice cho Developers

Khi gọi bất kỳ endpoint v1 nào, response sẽ kèm theo:

### HTTP Headers (RFC 8594)

```
Deprecation: true
Sunset: 2026-12-31
Link: </api/v2/payments>; rel="successor-version",
      <https://docs.example.com/migration/v1-to-v2>; rel="deprecation"
Warning: 299 - "This API version is deprecated. Please migrate to
          /api/v2/payments before 2026-12-31."
```

Xem headers thực tế:

```bash
curl -si http://localhost:8080/api/v1/payments | \
  grep -E "Deprecation|Sunset|Warning|Link"
```

### Body Warning (JSON)

Ngoài headers, response body v1 luôn có thêm key `_deprecation_warning`:

```json
{
  "_deprecation_warning": {
    "message": "This API version (v1) is deprecated and will be removed on 2026-12-31. Please migrate to /api/v2/payments.",
    "sunset_date": "2026-12-31",
    "migration_guide": "https://docs.example.com/migration/v1-to-v2",
    "successor": "/api/v2/payments"
  },
  "id": 1,
  "amount": 19.99,
  ...
}
```

---

## 8. So sánh các chiến lược

| Tiêu chí | URL Versioning | Header Versioning | Query Param |
|----------|---------------|-------------------|-------------|
| **Ví dụ** | `/api/v2/payments` | `API-Version: v2` | `?version=v2` |
| **Cache-friendly** | Có (URL unique) | Phụ thuộc Vary header | Có |
| **Dễ test trên browser** | Có | Không | Có |
| **URL ổn định** | Không (thay đổi theo version) | Có | Có |
| **Khả năng phát hiện** | Cao | Thấp | Trung bình |
| **Chuẩn HTTP** | Trung bình | Cao (content negotiation) | Thấp |
| **Phù hợp với** | Public API, long support | Internal API, SDK | Dev portal, prototyping |
| **Khuyến nghị** | Mặc định cho hầu hết API | Khi client kiểm soát headers | Chỉ cho testing |

### Khuyến nghị thực tế

> **Dùng URL versioning làm chiến lược chính** vì nó rõ ràng nhất, dễ
> document nhất, và cache-friendly. Chỉ dùng header hoặc query param khi
> có yêu cầu cụ thể (SDK internal, A/B testing, dev portal).

---

## Tài liệu tham khảo

- [RFC 8594 — The Sunset HTTP Header Field](https://www.rfc-editor.org/rfc/rfc8594)
- [RFC 7240 — Prefer Header for HTTP](https://www.rfc-editor.org/rfc/rfc7240)
- James Higginbotham — *Principles of Web API Design*, Chương 8
