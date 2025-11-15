import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
# Secret key for JWT (keep it secret!)
SECRET_KEY = os.getenv("SECRET_KEY")

def generate_token(user_id, expires_in=24):
    """
    Generate a JWT token valid for `expires_in` hours
    """
    payload = {
        "user_id": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=expires_in)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def decode_token(token):
    """
    Decode JWT token and return payload.
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError if invalid.
    """
    import jwt
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload
