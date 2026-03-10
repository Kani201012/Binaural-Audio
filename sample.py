import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import os

SAMPLE_RATE = 44100
CARRIER = 200 # Standard binaural carrier
DUR = 180 # 3 minutes

def gen_binaural(duration, start_f, end_f):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freqs = np.linspace(start_f, end_f, len(t))
    phase = 2 * np.pi * np.cumsum(freqs) / SAMPLE_RATE
    l = np.sin(2 * np.pi * CARRIER * t - phase/2)
    r = np.sin(2 * np.pi * CARRIER * t + phase/2)
    return (np.vstack((l, r)).T * 6000).astype(np.int16) 

def gen_white_noise(duration):
    # Crisp noise that we will filter into rain and wind
    samples = int(SAMPLE_RATE * duration)
    n = np.random.normal(0, 0.4, samples)
    return (np.vstack((n, n)).T * 32767).astype(np.int16)

def gen_ocean_swells(duration):
    # Noise with realistic crashing wave patterns
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, False)
    n = np.random.normal(0, 0.4, samples)
    swell = (np.sin(2 * np.pi * 0.1 * t) + 1) / 2  # 10-second waves
    swell = swell ** 2 # Makes the peaks sharper like crashing waves
    return (np.vstack((n * swell, n * swell)).T * 32767).astype(np.int16)

def gen_space_pad(duration):
    # A beautiful, airy atmospheric chord (No melody, just a rich pad)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    c3 = np.sin(2 * np.pi * 130.81 * t)
    g3 = np.sin(2 * np.pi * 196.00 * t)
    c4 = np.sin(2 * np.pi * 261.63 * t)
    d4 = np.sin(2 * np.pi * 293.66 * t)
    
    # Mix chord and add slow "breathing" effect
    tone = (c3 + g3*0.8 + c4*0.6 + d4*0.5) / 4.0
    breath = (np.sin(2 * np.pi * 0.05 * t) + 1) / 2
    tone = tone * (0.6 + 0.4 * breath)
    return (np.vstack((tone, tone)).T * 12000).astype(np.int16)

print("Generating high-fidelity audio elements...")
wavfile.write("raw_bin.wav", SAMPLE_RATE, gen_binaural(DUR, 10, 14))
wavfile.write("raw_noise.wav", SAMPLE_RATE, gen_white_noise(DUR))
wavfile.write("raw_ocean.wav", SAMPLE_RATE, gen_ocean_swells(DUR))
wavfile.write("raw_pad.wav", SAMPLE_RATE, gen_space_pad(DUR))

print("Applying EQ Filters and Mixing...")
bin_a = AudioSegment.from_wav("raw_bin.wav") - 18  # Push vibration to the back

# RAIN: Cut extreme highs and lows for a soft rainfall sound
rain_a = AudioSegment.from_wav("raw_noise.wav").high_pass_filter(500).low_pass_filter(3000) - 10

# OCEAN: Cut the highs so it sounds deep and distant
ocean_a = AudioSegment.from_wav("raw_ocean.wav").low_pass_filter(800) - 8

# SPACE PAD: Beautiful atmospheric tone
pad_a = AudioSegment.from_wav("raw_pad.wav") - 12

# DEEP FOCUS BROWN NOISE: Heavily filtered background rumble
depth_a = AudioSegment.from_wav("raw_noise.wav").low_pass_filter(250) - 8

# MIX EVERYTHING
mix = rain_a.overlay(ocean_a).overlay(pad_a).overlay(depth_a).overlay(bin_a)

print("Adding Skydiving Wind...")
# WIND: Mid-range noise that fades in smoothly
wind = AudioSegment.from_wav("raw_noise.wav").high_pass_filter(1000).low_pass_filter(2500) - 10
wind = wind.fade_in(5000)
mix = mix.overlay(wind, position=120000) # Start at 2-minute mark

mix.fade_out(4000).export("Janka_Fixed_Sample.mp3", format="mp3", bitrate="320k")

# Cleanup
for f in ["raw_bin.wav", "raw_noise.wav", "raw_ocean.wav", "raw_pad.wav"]: os.remove(f)
print("Perfect Sample Created!")
