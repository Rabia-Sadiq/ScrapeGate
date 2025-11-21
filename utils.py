import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
# Secret key for JWT (keep it secret!)
SECRET_KEY = os.getenv("SECRET_KEY")

def generate_token(user_id, allowed_endpoints=None, max_requests=50, expires_minutes=60):
    payload = {
        "user_id": user_id,
        "allowed_endpoints": allowed_endpoints or ["/api/data"],  # default endpoint
        "max_requests": max_requests,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes)
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
