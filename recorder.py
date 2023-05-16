import requests
import record

def send_audio_for_recognition(audio_path):
    response = requests.post('http://localhost:5000/recognize', data={"audio_path": audio_path})
    print(response.json())

if __name__ == "__main__":
    while True:
        audio_path = "./demo.wav"
        print("Start speaking...")
        record.record_to_file(audio_path)
        print("Done recording")
        
        send_audio_for_recognition(audio_path)
