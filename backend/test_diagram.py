import requests
import json

url = "http://localhost:8000/api/diagram"
payload = {
    "session_id": "01dd92dd-8812-4f2b-9e3a-dba74b5f19aa",
    "message": "diagram"
}

try:
    print(f"Testing {url}...")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
