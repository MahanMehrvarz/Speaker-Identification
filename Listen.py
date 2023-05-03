import record
audio_path = "./demo.wav"
print("start speaking")
record.record_to_file(audio_path)
print("done recording"g)

print("starting recognition:")
import sprec
rec = sprec.Recognizer()
print(rec.find_speaker(audio_path))
print("done")
