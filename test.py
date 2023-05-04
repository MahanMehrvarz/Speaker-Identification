import record
import sprec
audio_path = "./demo.wav"
print("start speaking")

rec = sprec.Recognizer()

while True:
    print("Start speaking")
    record_to_file(audio_path)
    print("Done recording")

    print("Starting recognition:")
    speaker_id = rec.find_speaker(audio_path)
    print(f"Speaker ID: {speaker_id}")
    print("Recognition done")