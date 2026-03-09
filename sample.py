import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import os

SAMPLE_RATE = 44100
CARRIER = 200
DUR = 180 # 3 Minute Showcase

def gen_binaural(duration, start_f, end_f):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freqs = np.linspace(start_f, end_f, len(t))
    phase = 2 * np.pi * np.cumsum(freqs) / SAMPLE_RATE
    l = np.sin(2 * np.pi * CARRIER * t - phase/2)
    r = np.sin(2 * np.pi * CARRIER * t + phase/2)
    return (np.vstack((l, r)).T * 32767).astype(np.int16)

def gen_brown(duration, vol=10000):
    samples = int(SAMPLE_RATE * duration)
    b = np.cumsum(np.random.uniform(-1, 1, samples))
    b /= np.max(np.abs(b))
    return (np.vstack((b, b)).T * vol).astype(np.int16)

def gen_ocean(duration):
    samples = int(SAMPLE_RATE * duration)
    b = np.cumsum(np.random.uniform(-1, 1, samples))
    b /= np.max(np.abs(b))
    t = np.linspace(0, duration, samples, False)
    swell = (np.sin(2 * np.pi * 0.1 * t) + 1) / 2 # Wave swell every 10s
    return (np.vstack((b*swell, b*swell)).T * 12000).astype(np.int16)

def gen_space_pad(duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    # Scientific non-melodic drone
    tone = (np.sin(2 * np.pi * 100 * t) + 0.4 * np.sin(2 * np.pi * 150 * t))
    tone /= np.max(np.abs(tone))
    return (np.vstack((tone, tone)).T * 7000).astype(np.int16)

# Generate Layers
wavfile.write("s_bin.wav", SAMPLE_RATE, gen_binaural(DUR, 10, 14))
wavfile.write("s_ocean.wav", SAMPLE_RATE, gen_ocean(DUR))
wavfile.write("s_pad.wav", SAMPLE_RATE, gen_space_pad(DUR))
wavfile.write("s_depth.wav", SAMPLE_RATE, gen_brown(DUR, 6000))

# Mix in Pydub
bin_a = AudioSegment.from_wav("s_bin.wav") - 22
oce_a = AudioSegment.from_wav("s_ocean.wav") - 12 # Rain/Ocean effect
pad_a = AudioSegment.from_wav("s_pad.wav") - 18  # Space ambience
dep_a = AudioSegment.from_wav("s_depth.wav").low_pass_filter(500) - 25 # Brown noise depth

# 100% COMPLIANT MIX
mix = oce_a.overlay(pad_a).overlay(dep_a).overlay(bin_a)

# Add Sky/Wind Texture in final 60 seconds (for the sample)
wind_raw = gen_brown(60, 12000)
wavfile.write("s_wind.wav", SAMPLE_RATE, wind_raw)
wind = AudioSegment.from_wav("s_wind.wav").high_pass_filter(1500).fade_in(5000) - 15
mix = mix.overlay(wind, position=120000) # Starts at 2:00 mark

# Export
mix.fade_out(5000).export("Janka_Technical_Sample.mp3", format="mp3", bitrate="320k")

# Cleanup
for f in ["s_bin.wav", "s_ocean.wav", "s_pad.wav", "s_depth.wav", "s_wind.wav"]: os.remove(f)
