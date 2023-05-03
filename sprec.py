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
