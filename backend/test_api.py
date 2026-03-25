import requests

url = "http://127.0.0.1:8000/chat"
payload = {
    "user_id": "test_user_ai_123",
    "message": "Teach me about Python Lists",
    "profile_id": "test_user_ai_123"
}

print("Sending chat request to the API...")
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print("Response Text:")
print(response.text)
