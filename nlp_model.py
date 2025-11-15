<<<<<<< HEAD
import pickle
from pathlib import Path

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "nlp_model.pkl"
VECTORIZER_PATH = BASE_DIR / "tfidf_vectorizer.pkl"

# Load model & vectorizer
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(VECTORIZER_PATH, "rb") as f:
    vectorizer = pickle.load(f)

def classify_text(text):
    """
    Classify text as VALID or INVALID using the trained model.
    """
    # Convert single text to proper 2D array
    X = vectorizer.transform([text])  # <-- wrap text in list
    prediction = model.predict(X)[0]
    
    # Get confidence / probability
    if hasattr(model, "predict_proba"):
        confidence = model.predict_proba(X).max()
    else:
        confidence = 1.0  # fallback if model has no predict_proba

    return prediction, confidence
=======
import pickle
from pathlib import Path

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "nlp_model.pkl"
VECTORIZER_PATH = BASE_DIR / "tfidf_vectorizer.pkl"

# Load model & vectorizer
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(VECTORIZER_PATH, "rb") as f:
    vectorizer = pickle.load(f)

def classify_text(text):
    """
    Classify text as VALID or INVALID using the trained model.
    """
    # Convert single text to proper 2D array
    X = vectorizer.transform([text])  # <-- wrap text in list
    prediction = model.predict(X)[0]
    
    # Get confidence / probability
    if hasattr(model, "predict_proba"):
        confidence = model.predict_proba(X).max()
    else:
        confidence = 1.0  # fallback if model has no predict_proba

    return prediction, confidence
>>>>>>> 7f79ef2b (phase 2)
