import requests
r = requests.post("http://localhost:8000/login?email=matheus3@test.com&password=123456")
headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
r = requests.get("http://localhost:8000/groups/1/streak", headers=headers)
print(r.json())

