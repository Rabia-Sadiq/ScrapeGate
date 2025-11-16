import requests
import time

BASE_URL = "http://127.0.0.1:5000"

print("\n==============================")
print(" PHASE 1 — Testing /detect")
print("==============================")
r = requests.get(f"{BASE_URL}/detect")
print("Status:", r.status_code)
print("Response:", r.text, "\n")

# ---------------------------------------------------------
print("==============================")
print(" PHASE 2 — /request-access + NLP")
print("==============================")

test_justifications = [
    "I need this data for academic research.",
    "Just want to scrape for fun."
]

tokens = []

for text in test_justifications:
    payload = {"justification": text}
    r = requests.post(f"{BASE_URL}/request-access", json=payload)
    data = r.json()

    print(f"\nJustification: {text}")
    print("Classification:", data.get("classification"))
    print("Confidence:", data.get("confidence"))

    if "token" in data:
        print("✔ Token Issued")
        tokens.append(data["token"])
    else:
        print("❌ Token Not Issued")

# ---------------------------------------------------------
print("\n==============================")
print(" PHASE 3 — Test Protected /api/data")
print("==============================")

for token in tokens:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/data", headers=headers)
    print(f"Token ({token[:10]}...): {r.status_code}")
    print("Response:", r.text, "\n")

# ---------------------------------------------------------
print("==============================")
print(" PHASE 4A — Excessive Requests (IP Block Test)")
print("==============================")

for i in range(15):
    r = requests.get(f"{BASE_URL}/detect")
    print(f"Request {i+1}: {r.status_code}")
    time.sleep(0.1)

print("\nTest blocked IP → POST /request-access")
payload = {"justification": "Retry after block"}
r = requests.post(f"{BASE_URL}/request-access", json=payload)
print("Status:", r.status_code)
print("Response:", r.text)

if tokens:
    print("\nTest blocked IP → /api/data with valid token")
    r = requests.get(f"{BASE_URL}/api/data", headers={"Authorization": f"Bearer {tokens[0]}"})
    print("Status:", r.status_code)
    print("Response:", r.text)

# ---------------------------------------------------------
print("\n==============================")
print(" PHASE 4B — Suspicious User-Agent Detection")
print("==============================")

suspicious_agents = [
    {"User-Agent": "curl/7.68.0"},
    {"User-Agent": "python-requests"},
    {"User-Agent": "Googlebot/2.1"}
]

for i, hdr in enumerate(suspicious_agents, 1):
    r = requests.get(f"{BASE_URL}/detect", headers=hdr)
    print(f"Test Suspicious UA {i}: {r.status_code}")
    print("Response:", r.text, "\n")

# ---------------------------------------------------------
print("==============================")
print(" OPTIONAL — Rate Limiting Test")
print("==============================")

if tokens:
    headers = {"Authorization": f"Bearer {tokens[0]}"}
    for i in range(10):
        r = requests.get(f"{BASE_URL}/api/data", headers=headers)
        print(f"RateLimit Request {i+1}: {r.status_code}")
        time.sleep(0.5)

# ---------------------------------------------------------
print("\n==============================")
print(" PHASE 5 — Admin Dashboard Tests")
print("==============================")

# Test Admin Landing Page
print("\nTest: GET /admin")
r = requests.get(f"{BASE_URL}/admin")
print("Status:", r.status_code)

# Test Tokens Table
print("\nTest: GET /admin/tokens")
r = requests.get(f"{BASE_URL}/admin/tokens")
print("Status:", r.status_code)

# Test Logs Table
print("\nTest: GET /admin/logs")
r = requests.get(f"{BASE_URL}/admin/logs")
print("Status:", r.status_code)

# Test Traffic Data API
print("\nTest: GET /api/admin/traffic-data")
r = requests.get(f"{BASE_URL}/api/admin/traffic-data")
print("Status:", r.status_code)
print("Traffic Data:", r.text)

# Test Token Revocation (if admin endpoint exists)
if tokens:
    print("\nTest: POST /admin/revoke/<token>")
    revoke_url = f"{BASE_URL}/admin/revoke/{tokens[0]}"
    r = requests.post(revoke_url)
    print("Status:", r.status_code)
    print("Response:", r.text)

    print("\nVerify revoked token cannot access /api/data")
    r = requests.get(f"{BASE_URL}/api/data", headers={"Authorization": f"Bearer {tokens[0]}"})
    print("Status:", r.status_code)
    print("Response:", r.text)
