from functools import wraps
from flask import request, jsonify
from utils import decode_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check header first
        if "Authorization" in request.headers:
            bearer = request.headers["Authorization"]
            if bearer.startswith("Bearer "):
                token = bearer.split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            payload = decode_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                raise ValueError("Invalid token payload")
        except Exception as e:
            return jsonify({"error": f"Token is invalid: {str(e)}"}), 401

        # Pass user_id to the route
        return f(user_id=user_id, *args, **kwargs)

    return decorated
