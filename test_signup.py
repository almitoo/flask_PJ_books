import requests

data = {
    "full_name": "John Doe",
    "email": "john@example.com",
    "mobile": "123456789",
    "password": "mypassword"
}

res = requests.post("http://127.0.0.1:5000/api/auth/signup", json=data)
print("Status Code:", res.status_code)
print("Response:", res.json())
