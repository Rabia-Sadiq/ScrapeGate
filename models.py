# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()  # Initialize here, app will bind later

# -----------------------------
# Phase 1 — Request Logging
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

# -----------------------------
# Phase 2 — Access Request / NLP
# -----------------------------
class AccessRequest(db.Model):
    __tablename__ = "access_requests"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45))
    justification = db.Column(db.Text)
    classification = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -----------------------------
# Phase 4 — Optional Blocked IP
# -----------------------------
class BlockedIP(db.Model):
    __tablename__ = "blocked_ips"
    ip = db.Column(db.String(45), primary_key=True)
    reason = db.Column(db.String(255))
    blocked_at = db.Column(db.DateTime, default=datetime.utcnow)
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    user_ip = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
# models.py
class APIEndpoint(db.Model):
    __tablename__ = "api_endpoints"
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100), unique=True, nullable=False)  # endpoint path
    description = db.Column(db.String(255), nullable=True)         # short description
    requires_validation = db.Column(db.Boolean, default=True)     # if access requires approval
