import torch
import numpy as np
import random
import pdb
import os
import threading
import time
import math
import glob
from scipy import signal
from scipy.io import wavfile
from torch.utils.data import Dataset, DataLoader
from utils import loadWAV


def round_down(num, divisor):
    return num - (num % divisor)


def worker_init_fn(worker_id):
    np.random.seed(np.random.get_state()[1][0] + worker_id)


class AugmentWAV(object):

    def __init__(self, musan_path, rir_path, max_frames):
        super(AugmentWAV, self).__init__()
        self.max_frames = max_frames
        self.max_audio = max_audio = max_frames * 160 + 240
        self.noisetypes = ['noise', 'speech', 'music']
        self.noisesnr = {'noise': [0, 15], 'speech': [13, 20], 'music': [5, 15]}
        self.numnoise = {'noise': [1, 1], 'speech': [3, 7], 'music': [1, 1]}
        self.noiselist = {}
        augment_files = glob.glob(os.path.join(musan_path, '*/*/*/*.wav'))

        for file in augment_files:
            if not file.split('/')[-4] in self.noiselist:
                self.noiselist[file.split('/')[-4]] = []
            self.noiselist[file.split('/')[-4]].append(file)

        self.rir_files = glob.glob(os.path.join(rir_path, '*/*/*.wav'))

    def additive_noise(self, noisecat, audio):
        clean_db = 10 * np.log10(np.mean(audio ** 2) + 1e-4)
        numnoise = self.numnoise[noisecat]
        noiselist = random.sample(self.noiselist[noisecat], random.randint(numnoise[0], numnoise[1]))
        noises = []

        for noise in noiselist:
            noiseaudio = loadWAV(noise, self.max_frames, evalmode=False)
            noise_snr = random.uniform(self.noisesnr[noisecat][0], self.noisesnr[noisecat][1])
            noise_db = 10 * np.log10(np.mean(noiseaudio[0] ** 2) + 1e-4)
            noises.append(np.sqrt(10 ** ((clean_db - noise_db - noise_snr) / 10)) * noiseaudio)

        return np.sum(np.concatenate(noises, axis=0), axis=0, keepdims=True) + audio

    def reverberate(self, audio):
        rir_file = random.choice(self.rir_files)
        fs, rir = wavfile.read(rir_file)
        rir = np.expand_dims(rir.astype(np.float), 0)
        rir = rir / np.sqrt(np.sum(rir ** 2))
        return signal.convolve(audio, rir, mode='full')[:, :self.max_audio]

    def speed_up(self, audio):
        audio = audio[0].astype(np.int16)
        return np.expand_dims(self.speedup.build_array(input_array=audio, sample_rate_in=16000), 0).astype(np.float)[:, :self.max_audio]

    def slow_down(self, audio):
        audio = audio[0].astype(np.int16)
        return np.expand_dims(self.slowdown.build_array(input_array=audio, sample_rate_in=16000), 0).astype(np.float)[:, :self.max_audio]


class VoxCelebDataset(Dataset):
    def __init__(self,
                 dataset_file_name,
                 augment,
                 musan_path,
                 rir_path,
                 max_frames,
                 train_path):
        super(VoxCelebDataset, self).__init__()
        self.augment_wav = AugmentWAV(musan_path=musan_path, rir_path=rir_path, max_frames=max_frames)
        self.dataset_file_name = dataset_file_name
        self.max_frames = max_frames
        self.musan_path = musan_path
        self.rir_path = rir_path
        self.augment = augment

        with open(dataset_file_name) as dataset_file:
            lines = dataset_file.readlines()

        dictkeys = list(set([x.split()[0] for x in lines]))
        dictkeys.sort()
        dictkeys = {key: ii for ii, key in enumerate(dictkeys)}

        self.label_dict = {}
        self.data_list = []
        self.data_label = []

        for lidx, line in enumerate(lines):
            data = line.strip().split()

            speaker_label = dictkeys[data[0]]
            filename = os.path.join(train_path, data[1])

            if not (speaker_label in self.label_dict):
                self.label_dict[speaker_label] = []

            self.label_dict[speaker_label].append(lidx)

            self.data_label.append(speaker_label)
            self.data_list.append(filename)

    def __getitem__(self, indices):
        squeeze = False
        if isinstance(indices, int):
            squeeze = True
            indices = [indices]

        feat = []
        for index in indices:
            audio = loadWAV(self.data_list[index], self.max_frames, evalmode=False)

            if self.augment:
                augtype = random.randint(0, 4)
                if augtype == 1:
                    audio = self.augment_wav.reverberate(audio)
                elif augtype == 2:
                    audio = self.augment_wav.additive_noise('music', audio)
                elif augtype == 3:
                    audio = self.augment_wav.additive_noise('speech', audio)
                elif augtype == 4:
                    audio = self.augment_wav.additive_noise('noise', audio)

            feat.append(audio)

        feat = np.concatenate(feat, axis=0)
        if squeeze:
            feat = feat[0]
        return torch.FloatTensor(feat), self.data_label[index]

    def __len__(self):
        return len(self.data_list)


class VoxCelebSampler(torch.utils.data.Sampler):
    def __init__(self, data_source: torch.utils.data.Dataset,
                 nPerSpeaker,
                 max_seg_per_spk,
                 batch_size: int):
        super(VoxCelebSampler, self).__init__(data_source)

        self.label_dict = data_source.label_dict
        self.nPerSpeaker = nPerSpeaker
        self.max_seg_per_spk = max_seg_per_spk
        self.batch_size = batch_size

    def __iter__(self):
        dictkeys = list(self.label_dict.keys())
        dictkeys.sort()
        lol = lambda lst, sz: [lst[i:i + sz] for i in range(0, len(lst), sz)]
        flattened_list = []
        flattened_label = []

        for findex, key in enumerate(dictkeys):
            data = self.label_dict[key]
            numSeg = round_down(min(len(data), self.max_seg_per_spk), self.nPerSpeaker)

            rp = lol(np.random.permutation(len(data))[:numSeg], self.nPerSpeaker)
            flattened_label.extend([findex] * (len(rp)))
            for indices in rp:
                flattened_list.append([data[i] for i in indices])

        mixid = np.random.permutation(len(flattened_label))
        mixlabel = []
        mixmap = []

        for ii in mixid:
            start_batch = len(mixlabel) - len(mixlabel) % self.batch_size
            if flattened_label[ii] not in mixlabel[start_batch:]:
                mixlabel.append(flattened_label[ii])
                mixmap.append(ii)

        return iter([flattened_list[i] for i in mixmap])

    def __len__(self):
        return len(self.data_source)


def get_data_loader(dataset_file_name, batch_size, augment, musan_path, rir_path, max_frames, max_seg_per_spk,
                    nDataLoaderThread, nPerSpeaker, train_path, **kwargs):
    train_dataset = VoxCelebDataset(dataset_file_name,
                                    augment,
                                    musan_path,
                                    rir_path,
                                    max_frames,
                                    train_path)

    train_sampler = VoxCelebSampler(train_dataset,
                                    nPerSpeaker,
                                    max_seg_per_spk,
                                    batch_size)

    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        num_workers=nDataLoaderThread,
        sampler=train_sampler,
        pin_memory=False,
        worker_init_fn=worker_init_fn,
        drop_last=True,
    )

    return train_loader
