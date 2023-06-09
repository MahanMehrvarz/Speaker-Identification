import logging
import nemo
import nemo.collections.asr as nemo_asr
import numpy as np
import torch
import glob
import itertools
import os
import pickle

class Recognizer():

    def __init__(self, datadir=None):
        self.speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained("nvidia/speakerverification_en_titanet_large")
        self.cosine_dist   = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        if datadir is None:
            datadir = os.path.join(self.base_path, "Data")
        self.speakers = os.listdir(datadir)

        self.thresh = 0.5

        # Load precomputed embeddings from disk
        self.embeddings = self.load_embeddings()

    def compute_and_save_embeddings(self):
        embeddings = {}
        for speaker in self.speakers:
            files_src = os.listdir(os.path.join(self.base_path, "Data", speaker))
            for file in files_src:
                if not file.lower().endswith('.wav'):
                    continue

                emb = self.speaker_model.get_embedding(os.path.join(self.base_path, "Data", speaker, file))
                embeddings[file] = emb

        with open('embeddings.pkl', 'wb') as f:
            pickle.dump(embeddings, f)

    def load_embeddings(self):
        if not os.path.exists('embeddings.pkl'):
            print('embeddings.pkl not found. Computing and saving embeddings...')
            self.compute_and_save_embeddings()

        with open('embeddings.pkl', 'rb') as f:
            embeddings = pickle.load(f)
        return embeddings


    def find_speaker(self, v1):
        emb1 = self.speaker_model.get_embedding(v1)
        n_corrects = {}
        for speaker in self.speakers:
            files_src = [f for f in os.listdir(os.path.join(self.base_path, "Data", speaker)) if not f.lower().endswith('.jpg')]
            n_corrects[speaker] = 0
            for file in files_src:
                # Use precomputed embedding
                emb2 = self.embeddings[file]
                if float(self.cosine_dist(emb1, emb2)) > self.thresh:
                    n_corrects[speaker] += 1
            n_corrects[speaker] = n_corrects[speaker] / len(files_src)

        best_id, best_per = None, 0
        print(n_corrects)
        for id_, per_ in n_corrects.items():
            if per_ >= 0.5:
                if per_ > best_per:
                    best_id = id_
                    best_per = per_
        return best_id

