import threading
import requests
from random import randint as r
import json

def hit():
    for _ in range(100):
        print((requests.get(f"http://localhost:8000/user/{r(0,10000)}").text))

threads = []

for _ in range(20):
    t = threading.Thread(target=hit)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("Done stress test")