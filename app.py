from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from nlp_model import classify_text   # ✅ your trained NLP model
from decorators import token_required
from utils import generate_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
from pathlib import Path

# -----------------------------
# Config
# -----------------------------
BASE_DIR = Path(__file__).parent
SQLITE_PATH = BASE_DIR / "requests.db"

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True

# -----------------------------
# App & DB Setup
# -----------------------------
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# -----------------------------
# Rate Limiter
# -----------------------------
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["20 per hour"]
)

# -----------------------------
# Database Models
# -----------------------------
class RequestLog(db.Model):
    __tablename__ = "request_logs"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45))
    path = db.Column(db.String(255))
    method = db.Column(db.String(10))
    headers = db.Column(db.Text)
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AccessRequest(db.Model):
    __tablename__ = "access_requests"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45))
    justification = db.Column(db.Text)
    classification = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables if they don’t exist
with app.app_context():
    db.create_all()

# -----------------------------
# Helper Function
# -----------------------------
def get_client_ip():
    """Extract real client IP (handles proxies)"""
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"

# -----------------------------
# Home Route
# -----------------------------
@app.route("/")
def home():
    return """
        <h1>ScrapGate Flask Server 🚀</h1>
        <p>Use <code>/detect</code> to log requests, or <code>/request-access</code> to test NLP classification.</p>
    """

# -----------------------------
# Phase 1 — Request Detection
# -----------------------------
@app.route("/detect", methods=["GET", "POST"])
def detect():
    ip = get_client_ip()
    path = request.path
    method = request.method
    headers_json = json.dumps(dict(request.headers))
    user_agent = request.headers.get("User-Agent", "")

    # Log request in DB
    log = RequestLog(ip=ip, path=path, method=method, headers=headers_json, user_agent=user_agent)
    db.session.add(log)
    db.session.commit()

    # Count number of recent requests from this IP
    window_minutes = int(request.args.get("window", 1))
    window_start = datetime.utcnow() - timedelta(minutes=window_minutes)
    count = RequestLog.query.filter(RequestLog.ip == ip, RequestLog.created_at >= window_start).count()

    return jsonify({
        "message": "Request logged ✅",
        "ip": ip,
        f"count_last_{window_minutes}_min": count,
        "timestamp": log.created_at.isoformat()
    }), 201

# -----------------------------
# Phase 2 + 3 — NLP Classification & Token Generation
# -----------------------------
@app.route("/request-access", methods=["GET", "POST"])
def request_access():
    if request.method == "GET":
        return render_template("request_access.html")

    if request.is_json:
        data = request.get_json(force=True)
        justification = data.get("justification", "").strip()
        user_id = data.get("user_id", get_client_ip())  # default to IP if not provided
    else:
        justification = request.form.get("justification", "").strip()
        user_id = get_client_ip()

    if not justification:
        return jsonify({"error": "Missing 'justification' field"}), 400

    # Run trained NLP model
    classification, confidence = classify_text(justification)

    # Save to DB
    new_entry = AccessRequest(
        ip=get_client_ip(),
        justification=justification,
        classification=classification,
        confidence=confidence
    )
    db.session.add(new_entry)
    db.session.commit()

    # Generate JWT token for valid requests
    token = generate_token(user_id) if classification.lower() == "valid" else None

    response = {
        "ip": get_client_ip(),
        "justification": justification,
        "classification": classification,
        "confidence": round(confidence, 3),
        "timestamp": new_entry.created_at.isoformat()
    }
    if token:
        response["token"] = token

    if request.is_json:
        return jsonify(response), 200 if classification.lower() == "valid" else 403
    else:
        return render_template(
            "request_access.html",
            result=f"Classification: {classification}, Confidence: {round(confidence,3)}",
            token=token
        )

# -----------------------------
# Phase 3 — Protected Route
# -----------------------------
@app.route("/api/data", methods=["GET"])
@token_required
@limiter.limit("5 per hour")  # optional per-route limit
def get_data(user_id):
    # user_id comes from token
    return jsonify({
        "message": f"Hello User {user_id}, here is your protected data.",
        "data": ["item1", "item2", "item3"]
    })

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    print("🚀 Server starting... Loading NLP model via nlp_model.py ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
