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
