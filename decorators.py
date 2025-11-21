from functools import wraps
from flask import request, jsonify
from utils import decode_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token missing"}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            allowed_endpoints = payload.get("allowed_endpoints", [])
            max_requests = payload.get("max_requests", 50)

            # Check if user can access this endpoint
            if request.path not in allowed_endpoints:
                return jsonify({"error": "Access to this endpoint is denied"}), 403

            # Optionally: track requests per token and enforce max_requests
            if not hasattr(request, "token_request_count"):
                request.token_request_count = {}
            count = request.token_request_count.get(token, 0)
            if count >= max_requests:
                return jsonify({"error": "Request limit exceeded"}), 429
            request.token_request_count[token] = count + 1

            kwargs["user_id"] = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated