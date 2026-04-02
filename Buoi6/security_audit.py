"""
=============================================================
  Library API - Security Audit Script
  Kiểm tra bảo mật API: lộ token, JWT vulnerabilities
=============================================================
"""

import requests
import json
import base64
import sys

BASE_URL = "http://127.0.0.1:8081"
PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
WARN = "\033[93m[WARN]\033[0m"
INFO = "\033[94m[INFO]\033[0m"

results = {"pass": 0, "fail": 0, "warn": 0}


def check(label, passed, detail="", warning=False):
    if warning:
        status = WARN
        results["warn"] += 1
    elif passed:
        status = PASS
        results["pass"] += 1
    else:
        status = FAIL
        results["fail"] += 1
    print(f"  {status} {label}")
    if detail:
        print(f"         └─ {detail}")


def section(title):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")


def decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verification."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(padded))
    except Exception:
        return {}


# ── Setup: create a test user and get a token ────────────────
section("0. SETUP - Tạo user và lấy token test")

EMAIL = "audit_test@example.com"
NAME = "Audit Test User"

# Create user (idempotent attempt)
r = requests.post(f"{BASE_URL}/api/users", json={"name": NAME, "email": EMAIL})
if r.status_code in (201, 409):
    print(f"  {INFO} Test user ready (status {r.status_code})")
else:
    print(f"  {FAIL} Cannot create test user: {r.status_code} {r.text}")
    sys.exit(1)

# Login
r = requests.post(f"{BASE_URL}/api/users/login", json={"email": EMAIL})
if r.status_code != 200 or "token" not in r.json():
    print(f"  {FAIL} Login failed: {r.status_code} {r.text}")
    sys.exit(1)

VALID_TOKEN = r.json()["token"]
AUTH = {"Authorization": f"Bearer {VALID_TOKEN}"}
print(f"  {INFO} Token obtained successfully")


# ── Test 1: Unauthenticated access ───────────────────────────
section("1. KIỂM TRA TRUY CẬP KHÔNG CÓ TOKEN")

PROTECTED = [
    ("GET",  "/api/users"),
    ("GET",  "/api/books"),
    ("GET",  "/api/loans"),
]

for method, path in PROTECTED:
    r = requests.request(method, f"{BASE_URL}{path}")
    check(
        f"{method} {path} → từ chối khi không có token",
        r.status_code == 401,
        f"HTTP {r.status_code} - {'OK' if r.status_code == 401 else r.text[:80]}"
    )

# ── Test 2: Token lộ ra trong response body ──────────────────
section("2. KIỂM TRA TOKEN KHÔNG BỊ LỘ TRONG RESPONSE")

endpoints = [
    ("GET",  "/api/users",  None),
    ("GET",  "/api/books",  None),
    ("GET",  "/api/loans",  None),
]

for method, path, body in endpoints:
    r = requests.request(method, f"{BASE_URL}{path}", headers=AUTH, json=body)
    raw = r.text.lower()
    leaked = any(kw in raw for kw in ["token", "secret", "password", "jwt", "bearer"])
    check(
        f"{method} {path} → không lộ token/secret trong body",
        not leaked,
        f"HTTP {r.status_code} | Leaked keywords detected!" if leaked else f"HTTP {r.status_code} | Clean"
    )

# ── Test 3: Token lộ trong response headers ──────────────────
section("3. KIỂM TRA TOKEN KHÔNG BỊ LỘ TRONG RESPONSE HEADERS")

r = requests.get(f"{BASE_URL}/api/users", headers=AUTH)
header_str = str(r.headers).lower()
check(
    "Token không xuất hiện trong response headers",
    "authorization" not in header_str and "bearer" not in header_str,
    f"Headers: {dict(r.headers)}"
)

# ── Test 4: Token trong URL / query string ───────────────────
section("4. KIỂM TRA TOKEN KHÔNG ĐƯỢC CHẤP NHẬN QUA URL PARAM")

r = requests.get(f"{BASE_URL}/api/users?token={VALID_TOKEN}")
check(
    "Token trong query string bị từ chối (không hỗ trợ ?token=)",
    r.status_code == 401,
    f"HTTP {r.status_code} - {'Safe: URL token not accepted' if r.status_code == 401 else 'RISK: URL token was accepted!'}"
)

# ── Test 5: Giả mạo token (tampered signature) ───────────────
section("5. KIỂM TRA TOKEN GIẢ MẠO / CHỮ KÝ SAI")

parts = VALID_TOKEN.split(".")
tampered = parts[0] + "." + parts[1] + ".invalidsignature"
r = requests.get(f"{BASE_URL}/api/users", headers={"Authorization": f"Bearer {tampered}"})
check(
    "Token bị sửa chữ ký → bị từ chối",
    r.status_code == 401,
    f"HTTP {r.status_code} | {r.json().get('msg', '')}"
)

# ── Test 6: Thuật toán "none" attack ─────────────────────────
section("6. KIỂM TRA TẤN CÔNG THUẬT TOÁN 'none' (alg=none)")

payload = decode_jwt_payload(VALID_TOKEN)
header_none = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b"=").decode()
payload_b64 = parts[1]
none_token = f"{header_none}.{payload_b64}."
r = requests.get(f"{BASE_URL}/api/users", headers={"Authorization": f"Bearer {none_token}"})
check(
    "Token với alg=none bị từ chối",
    r.status_code == 401,
    f"HTTP {r.status_code} | {r.json().get('msg', '')}"
)

# ── Test 7: Token rỗng / định dạng sai ───────────────────────
section("7. KIỂM TRA TOKEN RỖNG / ĐỊNH DẠNG SAI")

bad_tokens = [
    ("Chuỗi rỗng",          ""),
    ("Chữ 'null'",          "null"),
    ("Token chỉ 1 phần",    "abc"),
    ("Token 2 phần",        "abc.def"),
    ("Khoảng trắng",        "   "),
]

for label, bad_token in bad_tokens:
    r = requests.get(f"{BASE_URL}/api/users", headers={"Authorization": f"Bearer {bad_token}"})
    check(
        f"Bad token ({label}) → 401",
        r.status_code == 401,
        f"HTTP {r.status_code}"
    )

# ── Test 8: Thiếu header Authorization hoàn toàn ─────────────
section("8. KIỂM TRA THIẾU HEADER AUTHORIZATION")

r = requests.get(f"{BASE_URL}/api/users")
check(
    "Không có header Authorization → 401",
    r.status_code == 401,
    f"HTTP {r.status_code} | {r.json().get('msg', '')}"
)

# ── Test 9: JWT payload không lộ sensitive info ───────────────
section("9. KIỂM TRA NỘI DUNG JWT PAYLOAD KHÔNG CHỨA THÔNG TIN NHẠY CẢM")

payload = decode_jwt_payload(VALID_TOKEN)
print(f"  {INFO} JWT Payload decoded: {json.dumps(payload, indent=4)}")

sensitive_fields = ["password", "secret", "email", "name"]
leaked_fields = [f for f in sensitive_fields if f in payload]
check(
    "Payload không chứa password/secret",
    "password" not in payload and "secret" not in payload,
    f"Leaked sensitive fields: {leaked_fields}" if leaked_fields else "Clean"
)
check(
    "Payload không chứa email/name (PII)",
    "email" not in payload and "name" not in payload,
    f"PII exposed in token: {leaked_fields}" if leaked_fields else "Clean",
    warning=("email" in payload or "name" in payload)
)

# ── Test 10: Security headers ─────────────────────────────────
section("10. KIỂM TRA SECURITY HEADERS TRONG RESPONSE")

r = requests.get(f"{BASE_URL}/api/users", headers=AUTH)
security_headers = {
    "X-Content-Type-Options":  "nosniff",
    "X-Frame-Options":         None,
    "Content-Security-Policy": None,
    "Strict-Transport-Security": None,
}

for header, expected in security_headers.items():
    present = header in r.headers
    value = r.headers.get(header, "")
    if expected:
        ok = present and expected in value
    else:
        ok = present
    check(
        f"Header '{header}' có mặt",
        ok,
        f"Value: '{value}'" if present else "MISSING",
        warning=not ok
    )

# ── Test 11: Endpoint login không lộ token trong error ────────
section("11. KIỂM TRA ENDPOINT LOGIN KHÔNG LỘ THÔNG TIN SAI")

r = requests.post(f"{BASE_URL}/api/users/login", json={"email": "nonexistent@hack.com"})
check(
    "Login với email sai → 404 không lộ thêm thông tin",
    r.status_code == 404,
    f"HTTP {r.status_code} | Body: {r.text[:100]}"
)

r = requests.post(f"{BASE_URL}/api/users/login", json={})
check(
    "Login không có email → 400",
    r.status_code == 400,
    f"HTTP {r.status_code} | Body: {r.text[:100]}"
)

# ── Summary ───────────────────────────────────────────────────
section("📊 KẾT QUẢ KIỂM TRA BẢO MẬT")
total = results["pass"] + results["fail"] + results["warn"]
print(f"  Tổng số kiểm tra : {total}")
print(f"  \033[92mPASS\033[0m             : {results['pass']}")
print(f"  \033[91mFAIL\033[0m             : {results['fail']}")
print(f"  \033[93mWARN\033[0m             : {results['warn']}")
print()

if results["fail"] == 0:
    print("  \033[92m✓ API không có lỗ hổng lộ token nghiêm trọng.\033[0m")
else:
    print("  \033[91m✗ Phát hiện lỗ hổng! Xem các mục FAIL ở trên.\033[0m")

if results["warn"] > 0:
    print("  \033[93m⚠ Có một số cảnh báo cần xem xét thêm.\033[0m")
print()
