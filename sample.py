import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
from pydub.generators import WhiteNoise
import os

SAMPLE_RATE = 44100
DUR = 180  # 3 minutes

print("1. Generating Clean Scientific Binaural Beats...")
# Transition from 10Hz to 14Hz over 3 minutes
t = np.linspace(0, DUR, int(SAMPLE_RATE * DUR), False)
freqs = np.linspace(10, 14, len(t))
phase = 2 * np.pi * np.cumsum(freqs) / SAMPLE_RATE

# 200Hz Carrier Frequency
left = np.sin(2 * np.pi * 200 * t - phase/2)
right = np.sin(2 * np.pi * 200 * t + phase/2)
binaural = np.vstack((left, right)).T

# CRITICAL FIX: Lower volume to 10% so it doesn't vibrate the whole track!
wavfile.write("binaural_clean.wav", SAMPLE_RATE, (binaural * 3276).astype(np.int16))

print("2. Synthesizing Beautiful Space Pad...")
# C-Suspended Chord (C3, G3, C4, D4) - No melody, just a lush, calming atmosphere
c3 = np.sin(2 * np.pi * 130.81 * t)
g3 = np.sin(2 * np.pi * 196.00 * t)
c4 = np.sin(2 * np.pi * 261.63 * t)
d4 = np.sin(2 * np.pi * 293.66 * t)

pad = (c3 + g3 + c4 + d4) / 4.0
# Add a slow "breathing" swell every 20 seconds
swell = (np.sin(2 * np.pi * 0.05 * t) + 1) / 2 
pad = pad * (0.6 + 0.4 * swell) # Mix base volume with swell
pad = np.vstack((pad, pad)).T
wavfile.write("pad_clean.wav", SAMPLE_RATE, (pad * 6000).astype(np.int16))

print("3. Generating Organic Rain & Ocean using Studio Filters...")
bin_audio = AudioSegment.from_wav("binaural_clean.wav")
pad_audio = AudioSegment.from_wav("pad_clean.wav")

# Use Pydub's safe generator to avoid math clipping!
raw_noise = WhiteNoise().to_audio_segment(duration=DUR * 1000)

# Create Rain: Cut the harsh highs and muddy lows
rain = raw_noise.low_pass_filter(1500).high_pass_filter(400) - 20

# Create Deep Ocean Rumble (The Brown Noise requested)
ocean_rumble = raw_noise.low_pass_filter(300) - 12

print("4. Mixing the Final Track...")
# Stack the layers smoothly
mix = pad_audio.overlay(rain).overlay(ocean_rumble).overlay(bin_audio)

print("5. Adding the Skydiving Wind (Final 60 seconds)...")
# Create Wind: Focus on the "whoosh" frequencies
wind = raw_noise.high_pass_filter(800).low_pass_filter(2500) - 15

# Extract only the last 60 seconds and fade it in
wind_ending = wind[-60000:].fade_in(5000)

# Overlay the wind at exactly the 2-minute mark (120,000 milliseconds)
mix = mix.overlay(wind_ending, position=120000)

print("6. Exporting High-Quality MP3...")
mix.fade_out(5000).export("Janka_Perfect_Sample.mp3", format="mp3", bitrate="320k")

# Cleanup files
for f in ["binaural_clean.wav", "pad_clean.wav"]: os.remove(f)

print("SUCCESS! File saved as Janka_Perfect_Sample.mp3")
