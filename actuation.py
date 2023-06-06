import requests
import time

while True:
    try:
        response = requests.get('http://<api.py machine IP Address>:5000/latest_speaker')
        if response.status_code == 200:
            print(f"Latest speaker ID: {response.json()['id']}")
        else:
            print("No speakers found")
    except Exception as e:
        print(f"Error: {str(e)}")

    time.sleep(1)  # wait for 1 second before making the next request
