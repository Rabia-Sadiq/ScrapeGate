from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class RequestLog(db.Model):
    __tablename__ = "request_logs"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), index=True, nullable=False)
    path = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    headers = db.Column(db.Text, nullable=True)     # serialized headers (JSON string)
    user_agent = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
