import math, random
import torchaudio
from torchaudio import transforms
import torch
# from IPython.display import Audio
import matplotlib.pyplot as plt
# import IPython.core.debugger as db
# from pathlib import Path
from matplotlib.pyplot import specgram
import numpy as np

class AudioUtil():
  # ----------------------------
  # Load an audio file. Return the signal as a tensor and the sample rate
  # ----------------------------
  @staticmethod
  def open(audio_file):
    sig, sr = torchaudio.load(audio_file)
    return (sig, sr)
  
  # ----------------------------
  # Show a widget to play the audio sound
  # ----------------------------
  # @staticmethod
  #   def play(aud):
  #     sig,sr=aud
  #     display(Audio(data=sig, rate=sr))

  # ----------------------------
  # Pad (or trim) the signal to a fixed length 'max_ms' in milliseconds
  # ----------------------------
  @staticmethod
  def pad_trim(aud, max_ms):
    sig, sr = aud
    num_rows, sig_len = sig.shape
    max_len = sr//1000 * max_ms

    if (sig_len > max_len):
      # Trim the signal to the given length
      sig = sig[:,:max_len]

    elif (sig_len < max_len):
      # Length of padding to add at the beginning and end of the signal
      pad_begin_len = random.randint(0, max_len - sig_len)
      pad_end_len = max_len - sig_len - pad_begin_len

      # Pad with 0s
      pad_begin = torch.zeros((num_rows, pad_begin_len))
      pad_end = torch.zeros((num_rows, pad_end_len))

      sig = torch.cat((pad_begin, sig, pad_end), 1)
      
    return (sig, sr)

  # ----------------------------
  # Shifts the signal to the left or right by some percent. Values at the end
  # are 'wrapped around' to the start of the transformed signal.
  # ----------------------------
  @staticmethod
  def signal_shift(aud, max_shift_pct):
    sig,sr = aud
    roll_by = int(random.random()*max_shift_pct*len(sig[0]))
    return (sig.roll(roll_by), sr)

  # ----------------------------
  # Generate a Spectrogram
  # ----------------------------
  @staticmethod
  def spectro_gram(aud, spectro_type='mel', n_mels=64, n_fft=1024, hop_len=None):
    sig,sr = aud
    f_min, f_max, ws, top_db, pad = 0.0, None, None, 80, 0

    # spec has shape [channel, n_mels, time], where channel is mono, stereo etc
    if (spectro_type == 'mel'):
      spec = transforms.MelSpectrogram(sr, n_fft, ws, hop_len, f_min, f_max, pad, n_mels)(sig)
    elif (spectro_type == 'mfcc'):
      pass
    else: 
      spec = transforms.Spectrogram(n_fft, ws, hop_len, pad, normalize=False)(sig)

    # Convert to decibels
    spec = transforms.AmplitudeToDB(top_db=top_db)(spec)
    return (spec)


  # ----------------------------
  # Augment the Spectrogram by masking out some sections of it in both the frequency
  # dimension (ie. horizontal bars) and the time dimension (vertical bars) to prevent
  # overfitting and to help the model generalise better. The masked sections are
  # replaced with the mean value.
  # ----------------------------
  @staticmethod
  def spectro_augment(spec, max_mask_pct=0.1, n_freq_masks=1, n_time_masks=1):
    _, n_mels, n_steps = spec.shape

    # Frequency Masking: frequency channels [f0, f0 + f) are masked. f is chosen from a 
    # uniform distribution from 0 to the frequency mask parameter F, and f0 is chosen 
    # from (0, ν − f) where ν is the number of frequency channels.
    # Time Masking: t consecutive time steps [t0, t0 + t) are masked. t is chosen from a 
    # uniform distribution from 0 to the time mask parameter T, and t0 is chosen from [0, τ − t).

    # Max height of the frequency mask
    F = math.ceil(n_mels * max_mask_pct) # rounding up in case of small %
    # Max width of the time mask
    T = math.ceil(n_steps * max_mask_pct)

    # Create frequency masks
    fill = spec.mean()
    for i in range(0, n_freq_masks):
      f = random.randint(0, F)
      f0 = random.randint(0, n_mels-f)
      spec[0][f0:f0+f] = fill
    
    # Create time masks
    for i in range(0, n_time_masks):
      t = random.randint(0, T)
      t0 = random.randint(0, n_steps-t)
      spec[0][:,t0:t0+t] = fill
    return spec

  # ----------------------------
  # Plot the audio signal
  # ----------------------------
  @staticmethod
  def show_wave(aud, label='', ax=None):
    sig, sr = aud
    if (not ax):
      _,ax = plt.subplots(1, 1, figsize=(12, 3))
    ax.plot(sig[0])
    ax.set_title(label)
    plt.show()

  # ----------------------------
  # Plot the audio signal before and after a transform
  # ----------------------------
  @staticmethod
  def show_transform(orig, trans, label):
    osig,osr = orig
    tsig,tsr = trans
    if orig is not None: plt.plot(osig[0], 'm', label="Orig.")
    if trans is not None: plt.plot(tsig[0], 'c', alpha=0.5, label="Transf.")
    plt.title(label)
    plt.legend()
    plt.show()

  # ----------------------------
  # Plot the spectrogram
  # ----------------------------
  @staticmethod
  def show_spectro(spec, label='', ax=None, figsize=(6,6)):
    if (not ax):
      _,ax = plt.subplots(1, 1, figsize=figsize)
    # Reduce first dimension if it is greyscale
    ax.imshow(spec if (spec.shape[0]==3) else spec.squeeze(0))
    ax.set_title(f'{label}, {list(spec.shape)}')
    plt.show()