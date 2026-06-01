import requests
import time

url = "http://127.0.0.1:5000/data"

data = [
    {"temp":25,"humidity":60,"gas":100},
    {"temp":32,"humidity":70,"gas":250},
    {"temp":35,"humidity":80,"gas":500}
]

i=0
while True:
    requests.post(url,json=data[i])
    print("Sent:",data[i])
    i=(i+1)%3
    time.sleep(3)