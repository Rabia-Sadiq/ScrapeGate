import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
SQLITE_PATH = os.environ.get("SQLITE_PATH", BASE_DIR / "requests.db")

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
