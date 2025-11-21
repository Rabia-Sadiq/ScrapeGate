# scrapgate.py
import json
from datetime import datetime, timedelta
from flask import request, redirect, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, RequestLog, AccessRequest, APIEndpoint
from nlp_model import classify_text
from decorators import token_required
from utils import generate_token
from admin import admin_bp  # your admin blueprint


class ScrapGate:
    """
    ScrapGate middleware/plugin for Flask apps.

    Usage:
        from scrapgate import ScrapGate
        scrapgate = ScrapGate(app)
    """

    def __init__(self, app=None, request_threshold=10):
        self.blocked_ips = set()
        self.request_threshold = request_threshold
        self.request_log_cache = {}  # store requests per IP
        if app:
            self.init_app(app)

    def init_app(self, app):
        # Initialize DB with host app
        db.init_app(app)

        # Register admin blueprint
        app.register_blueprint(admin_bp, url_prefix="/")

        # Rate limiter
        Limiter(app=app, key_func=get_remote_address, default_limits=["20 per hour"])

        # Before request hook for suspicious users
        app.before_request(self.detect_suspicious_users)

        # Routes
        app.add_url_rule("/detect", "detect", self.detect, methods=["GET", "POST"])
        app.add_url_rule("/request-access", "request_access", self.request_access, methods=["GET", "POST"])
        app.add_url_rule("/api/data", "get_data", self.get_data, methods=["GET"])

    def get_client_ip(self):
        """Extract client IP, handles proxies"""
        xff = request.headers.get("X-Forwarded-For", "")
        if xff:
            return xff.split(",")[0].strip()
        return request.remote_addr or "unknown"

    # ------------------------
    # Suspicious User Detection
    # ------------------------
    def detect_suspicious_users(self):
        ip = self.get_client_ip()
        user_agent = request.headers.get("User-Agent", "").lower()

        # Skip access request route
        if request.endpoint == "request_access":
            return

        # Redirect blocked IPs
        if ip in self.blocked_ips:
            return redirect("/request-access")

        # Track requests in-memory per IP
        self.request_log_cache.setdefault(ip, [])
        now = datetime.utcnow()
        self.request_log_cache[ip].append(now)

        # Keep timestamps within last 1 min
        self.request_log_cache[ip] = [t for t in self.request_log_cache[ip] if now - t < timedelta(minutes=1)]

        # Block excessive requests
        if len(self.request_log_cache[ip]) > self.request_threshold:
            self.blocked_ips.add(ip)
            print(f"⚠️ Blocked {ip} for excessive requests")
            return redirect("/request-access")

        # Block suspicious User-Agent
        if "bot" in user_agent or "curl" in user_agent:
            self.blocked_ips.add(ip)
            print(f"⚠️ Blocked {ip} due to suspicious User-Agent: {user_agent}")
            return redirect("/request-access")

    # ------------------------
    # /detect route
    # ------------------------
    def detect(self):
        ip = self.get_client_ip()
        path = request.path
        method = request.method
        headers_json = json.dumps(dict(request.headers))
        user_agent = request.headers.get("User-Agent", "")

        # Log request in DB
        log = RequestLog(ip=ip, path=path, method=method, headers=headers_json, user_agent=user_agent)
        db.session.add(log)
        db.session.commit()

        # Count requests in last 1 min
        window_start = datetime.utcnow() - timedelta(minutes=1)
        count = RequestLog.query.filter(RequestLog.ip == ip, RequestLog.created_at >= window_start).count()

        return jsonify({
            "message": "Request logged ✅",
            "ip": ip,
            "count_last_1_min": count,
            "timestamp": log.created_at.isoformat()
        }), 201

    # ------------------------
    # /request-access route
    # ------------------------
    def request_access(self):
        ip = self.get_client_ip()
        token = None
        endpoints_info = []  # initialize to avoid UnboundLocalError

        if request.method == "GET":
            return render_template("request_access.html")

        # Handle JSON or form data
        if request.is_json:
            data = request.get_json(force=True)
            justification = data.get("justification", "").strip()
            user_id = data.get("user_id", ip)
        else:
            justification = request.form.get("justification", "").strip()
            user_id = ip

        if not justification:
            return jsonify({"error": "Missing 'justification' field"}), 400

        # NLP classification
        classification, confidence = classify_text(justification)

        # Save to DB
        new_entry = AccessRequest(
            ip=ip, justification=justification, classification=classification, confidence=confidence
        )
        db.session.add(new_entry)
        db.session.commit()

        # If valid, generate token & fetch allowed endpoints
        if classification.lower() == "valid":
            self.blocked_ips.discard(ip)

            # Fetch endpoints from DB
            allowed_endpoints = APIEndpoint.query.filter_by(requires_validation=True).all()
            endpoints_info = [{"path": ep.path, "description": ep.description} for ep in allowed_endpoints]

            # Generate JWT token (only include paths)
            token = generate_token(
                user_id,
                allowed_endpoints=[ep["path"] for ep in endpoints_info],
                max_requests=50
            )

        # Prepare response
        response = {
            "ip": ip,
            "justification": justification,
            "classification": classification,
            "confidence": round(confidence, 3),
            "allowed_endpoints": endpoints_info,  # safe now
            "timestamp": new_entry.created_at.isoformat()
        }
        if token:
            response["token"] = token

        # Return JSON or render HTML
        if request.is_json:
            return jsonify(response), 200 if classification.lower() == "valid" else 403
        else:
            return render_template(
                "request_access.html",
                result=f"Classification: {classification}, Confidence: {round(confidence,3)}",
                token=token,
                endpoints=endpoints_info
            )

    # ------------------------
    # /api/data route (protected)
    # ------------------------
    @token_required
    def get_data(self, user_id):
        return jsonify({
            "message": f"Hello User {user_id}, here is your protected data.",
            "data": ["item1", "item2", "item3"]
        })
