from app import app, db
from models import RequestLog
from sqlalchemy import func

with app.app_context():
    # Last 5 logs
    print("Last 5 logs:")
    last_logs = RequestLog.query.order_by(RequestLog.created_at.desc()).limit(5).all()
    for log in last_logs:
        print(f"{log.id} | {log.ip} | {log.path} | {log.method} | {log.created_at}")

    print("\nCounts per IP (last 1 minute):")
    window_minutes = 1
    from datetime import datetime, timedelta
    window_start = datetime.utcnow() - timedelta(minutes=window_minutes)

    counts = db.session.query(
        RequestLog.ip, func.count(RequestLog.id).label("count")
    ).filter(RequestLog.created_at >= window_start).group_by(RequestLog.ip).all()

    for ip, count in counts:
        print(f"{ip}: {count} request(s) in last {window_minutes} min")
