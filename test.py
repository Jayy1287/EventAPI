import requests
from requests.auth import HTTPBasicAuth

BASE = "http://127.0.0.1:5000/"

username = 'admin'
password = 'NicePassword'

#response = requests.get(BASE + "listEvents", {}, auth=HTTPBasicAuth(username, password))
#response = requests.put(BASE + "video/3?name=dfsf&location=asddf&capacity=123&date=12012024", {}, auth=HTTPBasicAuth(username, password))
#response = requests.get(BASE + "video/1", {}, auth=HTTPBasicAuth(username, password))
response = requests.get(BASE + "listAttendees", {}, auth=HTTPBasicAuth(username, password))

print(response.json())