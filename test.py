import requests
from requests.auth import HTTPBasicAuth

BASE = "http://127.0.0.1:5000/"

username = 'admin'
password = 'NicePassword'

response = requests.get(BASE + "video/1", {}, auth=HTTPBasicAuth(username, password))
print(response.json())