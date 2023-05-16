import record
import sprec

rec = sprec.Recognizer()

while True:
    audio_path = "./demo.wav"
    print("Start speaking...")
    record.record_to_file(audio_path)
    print("Done recording")

    print("Starting recognition:")
    speaker = rec.find_speaker(audio_path)
    print(f"Speaker: {speaker}")
    print("Recognition done\n")
