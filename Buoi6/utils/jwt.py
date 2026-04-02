import jwt
from flask import Flask, request, jsonify
import datetime
from functools import wraps

SECRET_KEY = "SECRET_KEY"

def create_access_token(sub: str, role: str):
    now = datetime.datetime.utcnow()

    payload = {
        "sub": str(sub),
        "role": role,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=30)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def parse_bearer_token():
    auth = request.headers.get("Authorization") or ""
    parts = auth.split()

    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]

    return None


def require_jwt(required_role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            token = parse_bearer_token()

            if not token:
                return jsonify({"msg": "Missing token"}), 401

            try:
                claims = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            except jwt.ExpiredSignatureError:
                return jsonify({"msg": "Token expired"}), 401

            except jwt.InvalidTokenError:
                return jsonify({"msg": "Invalid token"}), 401

            if required_role and claims.get("role") != required_role:
                return jsonify({"msg": "Forbidden"}), 403

            return f(claims, *args, **kwargs)

        return wrapper

    return decorator
