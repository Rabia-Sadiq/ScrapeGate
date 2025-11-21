# main_app.py
from flask import Flask
from scrapgate import ScrapGate
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

# Initialize ScrapGate plugin
scrapgate = ScrapGate(app)

# Optional: your own routes
@app.route("/")
def home():
    return "<h1>Welcome to my protected website!</h1>"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
