from app import app, db
from models import APIEndpoint

# ⚡ Wrap DB operations inside the application context
with app.app_context():
    db.create_all()  # creates tables if not exist

    # Add sample endpoints
    ep1 = APIEndpoint(path="/api/data", description="Get user data", requires_validation=True)
    ep2 = APIEndpoint(path="/api/orders", description="Get order info", requires_validation=True)
    ep3 = APIEndpoint(path="/public/info", description="Public info", requires_validation=False)

    db.session.add_all([ep1, ep2, ep3])
    db.session.commit()
    print("✅ Sample endpoints added successfully!")
