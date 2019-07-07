# -*- coding: utf-8 -*-
from argparse import Namespace
import glob
import numpy as np
import os
import pandas as pd
import python_speech_features  # NOQA
import soundfile
import sys


def load_locata_wav(fnames, obj_type):
    obj = Namespace()
    obj.data = dict()
    for this_wav in fnames:
        # Load data:
        data, fs = soundfile.read(this_wav)

        # Array name:
        this_obj = os.path.basename(this_wav).replace('.wav', '')
        this_obj = this_obj.replace('{}_'.format(obj_type), '')

        # Load timestamps:
        _txt_table = this_wav.replace('{}.wav'.format(this_obj),
                                      'timestamps_{}.txt'.format(this_obj))
        txt_table = np.loadtxt(_txt_table, delimiter='\t', skiprows=1).T

        # Copy to namespace:
        obj.fs = fs
        obj.data[str(this_obj)] = data
        obj.time = txt_table
    return obj


def load_locata_txt(fnames, obj_type):
    obj = Namespace()
    obj.data = dict()
    for this_txt in fnames:
        # Load data:
        txt_table = pd.read_csv(this_txt, sep='\t', header=0)
        _time = txt_table[['year', 'month', 'day',
                           'hour', 'minute', 'second']]
        _pos = txt_table[['x', 'y', 'z']].values.T
        _ref = txt_table[['ref_vec_x', 'ref_vec_x', 'ref_vec_x']].values.T
        _rot = txt_table[['rotation_11', 'rotation_12', 'rotation_13',
                          'rotation_21', 'rotation_22', 'rotation_23',
                          'rotation_31', 'rotation_32', 'rotation_33']].values.T
        mics = list(set([x.split('_')[0] for x in txt_table if 'mic' in x]))
        if len(mics) > 0:
            for i in range(len(mics)):
                _lbl = ['mic{}_{}'.format(i + 1, x) for x in ['x', 'y', 'z']]
                _data = txt_table[_lbl].values.T
                if i == 0:
                    _mic = np.zeros((3, _data.shape[1], len(mics)))
                _mic[:, :, i] = _data
        else:
            _mic = None

        # Array name:
        this_obj = os.path.basename(this_txt).replace('.txt', '')
        this_obj = this_obj.replace('{}_'.format(obj_type), '')

        # Copy to namespace:
        obj.time = pd.to_datetime(_time)
        obj.data[str(this_obj)] = Namespace(
            position=_pos, ref_vec=_ref, rotation=_rot,
            mic=_mic)
    return obj


def LoadLocataData(this_array, args, log, is_dev=True):
    """loads LOCATA csv and wav data

    Inputs:
        dir_name:     Directory name containing LOCATA data (default: ../data/)

    Outputs:
        audio_array:    Structure containing audio data recorded at each of the arrays
        audio_source:   Structure containing clean speech data
        position_array:   Structure containing positional information of each of the arrays
        position_source:  Structure containing positional information of each source
        required_time:    Structure containing the timestamps at which participants must provide estimates
    """

    # Time vector:
    txt_array = pd.read_csv(os.path.join(this_array, 'required_time.txt'),
                           sep='\t')
    _time = pd.to_datetime(txt_array[['year', 'month', 'day',
                               'hour', 'minute', 'second']])
    _valid = np.array(txt_array['valid_flag'].values, dtype=np.bool)
    required_time = Namespace(time=_time, valid_flag=_valid)

    # Audio files:
    wav_fnames = glob.glob(os.path.join(this_array, '*.wav'))

    audio_array_idx = [x for x in wav_fnames if 'audio_array' in x]
    if is_dev:
        audio_source_idx = [x for x in wav_fnames if 'audio_source' in x]
        if len(audio_array_idx) + len(audio_source_idx) == 0:
            log.error('Unexpected audio file in folder'.format(this_array))
            sys.exit(1)
    else:
        if len(audio_array_idx) == 0:
            log.error('Unexpected audio file in folder'.format(this_array))
            sys.exit(1)

    # Audio array data
    audio_array = load_locata_wav(audio_array_idx, 'audio_array')

    # Audio source data:
    if is_dev:
        audio_source = load_locata_wav(audio_source_idx, 'audio_source')
        audio_source.NS = len(audio_source.data)
    else:
        audio_source = None

    # Position source data:
    txt_fnames = glob.glob(os.path.join(this_array, '*.txt'))
    if is_dev:
        position_source_idx = [x for x in txt_fnames if 'position_source' in x]
        position_source = load_locata_txt(position_source_idx, 'position_source')
    else:
        position_source = None

    # Position array data:
    position_array_idx = [x for x in txt_fnames if 'position_array' in x]
    position_array = load_locata_txt(position_array_idx, 'position_array')

    # Outputs:
    return audio_array, audio_source, position_array, position_source, required_time

def GetLocataTruth(this_array, position_array, position_source, required_time, is_dev):
    return None

def LoadDCASEData(this_array, args, log, is_dev=True):
    pass