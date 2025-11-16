from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
from pathlib import Path

from models import db, RequestLog, AccessRequest, BlockedIP  # ✅ your separate models file
from nlp_model import classify_text  # ✅ your trained NLP model
from decorators import token_required
from utils import generate_token
from admin import admin_bp
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
db.init_app(app)
app.register_blueprint(admin_bp, url_prefix="/")
# -----------------------------
# Rate Limiter
# -----------------------------
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["20 per hour"]
)

# -----------------------------
# Phase 4 – Suspicious User Detection
# -----------------------------
blocked_ips = set()
REQUEST_THRESHOLD = 10  # max requests per minute

@app.before_request
def detect_suspicious_users():
    ip = request.remote_addr or "unknown"
    user_agent = request.headers.get("User-Agent", "").lower()

    # Skip request_access route
    if request.endpoint == "request_access":
        return

    # Redirect blocked IPs
    if ip in blocked_ips:
        return redirect("/request-access")

    # Track requests in-memory per IP
    if not hasattr(app, "request_log_cache"):
        app.request_log_cache = {}
    app.request_log_cache.setdefault(ip, [])
    now = datetime.utcnow()
    app.request_log_cache[ip].append(now)

    # Keep timestamps within last 1 min
    app.request_log_cache[ip] = [
        t for t in app.request_log_cache[ip] if now - t < timedelta(minutes=1)
    ]

    # Rule 1: Excessive requests → block
    if len(app.request_log_cache[ip]) > REQUEST_THRESHOLD:
        blocked_ips.add(ip)
        print(f"⚠️ Blocked {ip} for excessive requests")
        return redirect("/request-access")

    # Rule 2: Suspicious User-Agent → block
    if "bot" in user_agent or "curl" in user_agent:
        blocked_ips.add(ip)
        print(f"⚠️ Blocked {ip} due to suspicious User-Agent: {user_agent}")
        return redirect("/request-access")

# -----------------------------
# Helper Functions
# -----------------------------
def get_client_ip():
    """Extract real client IP (handles proxies)"""
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return """
        <h1>ScrapGate Flask Server 🚀</h1>
        <p>Use <code>/detect</code> to log requests, or <code>/request-access</code> to test NLP classification.</p>
    """

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
    count = RequestLog.query.filter(
        RequestLog.ip == ip, RequestLog.created_at >= window_start
    ).count()

    return jsonify({
        "message": "Request logged ✅",
        "ip": ip,
        f"count_last_{window_minutes}_min": count,
        "timestamp": log.created_at.isoformat()
    }), 201

@app.route("/request-access", methods=["GET", "POST"])
def request_access():
    if request.method == "GET":
        return render_template("request_access.html")

    # Handle JSON or form data
    if request.is_json:
        data = request.get_json(force=True)
        justification = data.get("justification", "").strip()
        user_id = data.get("user_id", get_client_ip())
    else:
        justification = request.form.get("justification", "").strip()
        user_id = get_client_ip()

    if not justification:
        return jsonify({"error": "Missing 'justification' field"}), 400

    # Run NLP model
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

    # Unblock IP if valid
    token = None
    if classification.lower() == "valid":
        blocked_ips.discard(get_client_ip())
        token = generate_token(user_id)

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

@app.route("/api/data", methods=["GET"])
@token_required
@limiter.limit("5 per hour")  # optional per-route limit
def get_data(user_id):
    return jsonify({
        "message": f"Hello User {user_id}, here is your protected data.",
        "data": ["item1", "item2", "item3"]
    })
@app.route('/api/admin/traffic-data')
def traffic_data():
    last_24h = datetime.utcnow() - timedelta(hours=24)
    logs = RequestLog.query.filter(RequestLog.timestamp >= last_24h).all()

    hourly = {}
    for log in logs:
        hour = log.timestamp.strftime("%H:00")
        hourly[hour] = hourly.get(hour, 0) + 1

    labels = list(hourly.keys())
    values = list(hourly.values())

    return jsonify({"labels": labels, "values": values})

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ensure tables exist
    print("🚀 Server starting... Loading NLP model via nlp_model.py ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
