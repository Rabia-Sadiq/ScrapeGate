import requests
import time

BASE_URL = "http://127.0.0.1:5000"

# -------- Phase 1: Detect route --------
print("=== Phase 1: Testing /detect route ===")
r = requests.get(f"{BASE_URL}/detect")
print(f"Status Code: {r.status_code}")
print(f"Response: {r.text}\n")

# -------- Phase 2: NLP Classification --------
print("=== Phase 2: Testing /request-access ===")
test_justifications = [
    "I need this data for academic research.",
    "Just want to scrape for fun."
]

tokens = []

for text in test_justifications:
    payload = {"justification": text}
    r = requests.post(f"{BASE_URL}/request-access", json=payload)
    data = r.json()
    print(f"Justification: {text}")
    print(f"Classification: {data.get('classification')}, Confidence: {data.get('confidence')}")
    if 'token' in data:
        tokens.append(data['token'])
    print()

# -------- Phase 3: Token Access Control --------
print("=== Phase 3: Testing token access to /api/data ===")
for token in tokens:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/data", headers=headers)
    print(f"Token: {token[:10]}... Status Code: {r.status_code}")
    print(f"Response: {r.text}\n")

# -------- Optional: Rate limiting test --------
print("=== Rate Limit Test ===")
if tokens:
    headers = {"Authorization": f"Bearer {tokens[0]}"}
    for i in range(10):  # Send multiple rapid requests
        r = requests.get(f"{BASE_URL}/api/data", headers=headers)
        print(f"Request {i+1} -> Status Code: {r.status_code}")
        time.sleep(0.5)  # Adjust based on your rate limit
