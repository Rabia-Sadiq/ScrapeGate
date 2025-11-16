
# 📌 **README.md — ScrapeGate: NLP-Driven Controlled Scraping Access**

## 🚀 Overview

**ScrapeGate** is an **Information Security semester project** designed to control and secure web-scraping access using NLP-based request classification, rate limiting, token-based authorization, and logging.

The system prevents **unauthorized, abusive, or malicious scraping**, while still allowing legitimate users to request access.

## 🧠 Key Features

### ✅ **1. NLP-Driven Justification Classification**

* Every user must submit a justification before gaining scraping access.
* A trained NLP model (TF-IDF + ML classifier) categorizes the justification as:

  * **Legitimate**
  * **Suspicious**
  * **Malicious**

### ✅ **2. Token-Based Access System**

* Only approved users receive a **secure JWT token**.
* The token is required to call protected routes.

### ✅ **3. Rate Limiting & Abuse Prevention**

* Each IP is tracked.
* Requests exceeding the threshold (e.g., > 60/min) are blocked.
* Abuse attempts are recorded.

### ✅ **4. Database Logging**

All events are stored:

* IP
* Timestamp
* Request count
* Justification
* Classification result

### ✅ **5. API Endpoints**

* `/detect` → logs a scraping attempt
* `/request-access` → submits textual justification
* `/get-token` → returns token if approved
* `/protected-resource` → only accessible via valid token

---

## 🗂 Project Structure

```
ScrapeGate/
│── app.py
│── models.py
│── nlp_model.py
│── utils.py
│── decorators.py
│── requirements.txt
│── README.md
│
├── static/
├── templates/
│   ├── index.html
│   ├── result.html
│
├── db.sqlite3
└── training/
    ├── dataset.csv
    ├── vectorizer.pkl
    └── classifier.pkl
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/ScrapeGate.git
cd ScrapeGate
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Flask App

```bash
python app.py
```

---

## 🧪 API Endpoints

### 🔍 **POST /detect**

Logs a request attempt.

**Response example:**

```json
{
  "message": "Request logged",
  "ip": "127.0.0.1",
  "count_last_1_min": 3
}
```

---

### 📝 **POST /request-access**

User submits justification.

```json
{
  "justification": "I need data for research"
}
```

**NLP Classification Response:**

```json
{
  "classification": "legitimate",
  "message": "Request approved. Get your token using /get-token"
}
```

---

### 🔐 **GET /get-token**

Returns JWT token for approved users.

---

### 🛡️ **GET /protected-resource**

Requires token:

```
Authorization: Bearer <token>
```

iagrams (Architecture / Flowchart / ERD)*
Just tell me **“create wiki”**, **“create slides”**, or **“make the diagram”**!
