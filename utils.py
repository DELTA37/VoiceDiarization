import numpy as np
import random
import pdb
import os
import threading
import time
import math
import glob
from scipy.io import wavfile


def loadWAV(filename,
            max_frames,
            evalmode=True,
            num_eval=10):
    # Maximum audio length
    max_audio = max_frames * 160 + 240
    sample_rate, audio = wavfile.read(filename)
    audiosize = audio.shape[0]

    if audiosize <= max_audio:
        shortage = max_audio - audiosize + 1
        audio = np.pad(audio, (0, shortage), 'wrap')
        audiosize = audio.shape[0]

    if evalmode:
        startframe = np.linspace(0, audiosize - max_audio, num=num_eval)
    else:
        startframe = np.array([np.int64(random.random() * (audiosize - max_audio))])

    feats = []
    if evalmode and max_frames == 0:
        feats.append(audio)
    else:
        for asf in startframe:
            feats.append(audio[int(asf):int(asf) + max_audio])

    feat = np.stack(feats, axis=0).astype(np.float)
    return feat
