import requests

url = "http://registrar-cellium.ngrok.app/upload"
body = {
    "data": "this is a atest"
}
headers = {
    "Content-Type": "application/json",
    "Authorization": "batman"
}

result = requests.post(url, json=body, headers=headers, verify=False)

print(result)