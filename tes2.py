import logging
logging.disable(logging.CRITICAL)
import nemo
import nemo.collections.asr as nemo_asr
import numpy as np
import torch
import glob
import itertools
import os

class Recognizer():

    def __init__(self, datadir="/home/mahan/Downloads/code/Data"):
        self.speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained("nvidia/speakerverification_en_titanet_large")
        self.cosine_dist   = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
        self.speakers      = os.listdir(datadir)
        self.thresh        = 0.5

    def find_speaker(self, v1):
        emb1 = self.speaker_model.get_embedding(v1)
        n_corrects = {}
        for speaker in self.speakers:
            files_src = os.listdir(f"./Data/{speaker}")
            n_corrects[speaker] = 0
            for file in files_src:
                emb2 = self.speaker_model.get_embedding(f"/home/mahan/Downloads/code/Data/{speaker}/{file}")
                if float(self.cosine_dist(emb1, emb2)) > self.thresh:
                    n_corrects[speaker] += 1
            n_corrects[speaker] = n_corrects[speaker]/len(files_src)

        best_id, best_per = None, 0
        print(n_corrects)
        for id_, per_ in n_corrects.items():
            if per_ >= 0.5:
                if per_ > best_per:
                    best_id = id_
                    best_per = per_
        return best_id

from ctypes import *
import pyaudio
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

asound = cdll.LoadLibrary('libasound.so.2')
# Set error handler
asound.snd_lib_error_set_handler(c_error_handler)


from sys import byteorder
from array import array
from struct import pack
#test
# import pyaudio
import wave

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    silence = [0] * int(seconds * RATE)
    r = array('h', silence)
    r.extend(snd_data)
    r.extend(silence)
    return r

def record():
    """
    Record a word or words from the microphone and 
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the 
    start and end, and pads with 0.5 seconds of 
    blank sound to make sure VLC et al can play 
    it without getting chopped off.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 70:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r

def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h'*len(data)), *data)
    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()


audio_path = "./demo.wav"
print("start speaking")

while True:
    print("Start speaking")
    record_to_file(audio_path)
    print("Done recording")

    print("Starting recognition:")
    speaker_id = rec.find_speaker(audio_path)
    print(f"Speaker ID: {speaker_id}")
    print("Recognition done")
