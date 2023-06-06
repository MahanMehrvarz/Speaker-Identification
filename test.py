import record
#import sprec
import sprecFast as sprec
rec = sprec.Recognizer()


# Compute and save embeddings - only do this when new audio files are added
rec.compute_and_save_embeddings()

while True:
    audio_path = "./demo.wav"
    print("Start speaking...")
    record.record_to_file(audio_path)
    print("Done recording")

    print("Starting recognition:")
    speaker = rec.find_speaker(audio_path)
    print(f"Speaker: {speaker}")
    print("Recognition done\n")
