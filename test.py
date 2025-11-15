import requests
import time

BASE_URL = "http://127.0.0.1:5000"

# -------- Phase 1: Detect route --------
print("=== Phase 1: Testing /detect route ===")
r = requests.get(f"{BASE_URL}/detect")
print(f"Status Code: {r.status_code}")
print(f"Response: {r.text}\n")

# -------- Phase 2: NLP Classification & Access Request --------
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

# -------- Phase 4: Suspicious User Detection (Excessive Requests) --------
print("=== Phase 4a: Testing Excessive Request Block ===")
for i in range(15):  # more than REQUEST_THRESHOLD
    r = requests.get(f"{BASE_URL}/detect")
    print(f"Request {i+1} -> Status Code: {r.status_code}")
    time.sleep(0.1)  # rapid requests

# Test blocked IP access
print("\nTesting blocked IP access to /request-access")
payload = {"justification": "Trying after being blocked"}
r = requests.post(f"{BASE_URL}/request-access", json=payload)
print(f"Status Code: {r.status_code}")
print(f"Response: {r.text}\n")

# Test blocked IP access to /api/data with valid token
print("Testing blocked IP access to /api/data with a valid token")
if tokens:
    headers = {"Authorization": f"Bearer {tokens[0]}"}
    r = requests.get(f"{BASE_URL}/api/data", headers=headers)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text}\n")

# -------- Phase 4: Suspicious User Detection (Suspicious User-Agent) --------
print("=== Phase 4b: Testing Suspicious User-Agent Block ===")
suspicious_headers = [
    {"User-Agent": "curl/7.68.0"},
    {"User-Agent": "Googlebot/2.1"}
]

for i, headers in enumerate(suspicious_headers, 1):
    r = requests.get(f"{BASE_URL}/detect", headers=headers)
    print(f"Suspicious Request {i} -> Status Code: {r.status_code}")
    print(f"Response: {r.text}\n")

# -------- Optional: Rate limiting test --------
print("=== Optional: Rate Limit Test ===")
if tokens:
    headers = {"Authorization": f"Bearer {tokens[0]}"}
    for i in range(10):  # send multiple rapid requests to hit limiter
        r = requests.get(f"{BASE_URL}/api/data", headers=headers)
        print(f"Rate Limit Test Request {i+1} -> Status Code: {r.status_code}")
        time.sleep(0.5)
