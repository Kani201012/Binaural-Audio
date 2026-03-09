import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import os

# --- SAMPLE CONFIGURATION ---
SAMPLE_RATE = 44100
CARRIER_FREQ = 200 
SAMPLE_DURATION = 180 # 3 Minutes

def generate_smooth_binaural(duration, sr, carrier):
    t = np.linspace(0, duration, int(sr * duration), False)
    freq_schedule = np.zeros_like(t)
    # Compressed schedule for the sample:
    # 0-60s: 10Hz | 60-120s: Ramp 10 to 14Hz | 120-180s: 14Hz
    freq_schedule[:60*sr] = 10
    freq_schedule[60*sr:120*sr] = np.linspace(10, 14, 60*sr)
    freq_schedule[120*sr:] = 14
    phase = 2 * np.pi * np.cumsum(freq_schedule) / sr
    left = np.sin(2 * np.pi * carrier * t - (phase / 2))
    right = np.sin(2 * np.pi * carrier * t + (phase / 2))
    return (np.vstack((left, right)).T * 32767).astype(np.int16)

# Reuse your previous helper functions for Brown Noise and Ocean Swells...
def generate_brown_noise(duration, volume=10000):
    samples = int(SAMPLE_RATE * duration)
    brown = np.cumsum(np.random.uniform(-1, 1, samples))
    brown /= np.max(np.abs(brown)); return (np.vstack((brown, brown)).T * volume).astype(np.int16)

print("Generating 3-minute Demo...")
# 1. Binaural
binaural = generate_smooth_binaural(SAMPLE_DURATION, SAMPLE_RATE, CARRIER_FREQ)
wavfile.write("s_bin.wav", SAMPLE_RATE, binaural)
# 2. Textures
brown = generate_brown_noise(SAMPLE_DURATION, 6000)
wavfile.write("s_brown.wav", SAMPLE_RATE, brown)

# Mix
bin_aud = AudioSegment.from_wav("s_bin.wav") - 20
brn_aud = AudioSegment.from_wav("s_brown.wav").low_pass_filter(500) - 25
demo = bin_aud.overlay(brn_aud)

# Add Wind at the very end of the sample to show that texture
wind_raw = generate_brown_noise(60, 12000)
wavfile.write("s_wind.wav", SAMPLE_RATE, wind_raw)
wind = AudioSegment.from_wav("s_wind.wav").high_pass_filter(1500).fade_in(5000) - 15
demo = demo.overlay(wind, position=120000) # Start wind at 2-minute mark

demo.fade_out(3000).export("Janka_ADHD_Project_SAMPLE.mp3", format="mp3", bitrate="320k")

# Cleanup
for f in ["s_bin.wav", "s_brown.wav", "s_wind.wav"]: os.remove(f)
print("Sample Created: Janka_ADHD_Project_SAMPLE.mp3")
