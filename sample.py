import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import os

SAMPLE_RATE = 44100
CARRIER = 200 
DUR = 180 

def gen_smooth_binaural(duration):
    # Smooth transition from 10Hz to 14Hz
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freqs = np.linspace(10, 14, len(t))
    phase = 2 * np.pi * np.cumsum(freqs) / SAMPLE_RATE
    l = np.sin(2 * np.pi * CARRIER * t - phase/2)
    r = np.sin(2 * np.pi * CARRIER * t + phase/2)
    return (np.vstack((l, r)).T * 32767).astype(np.int16)

def gen_true_brown_noise(duration, volume_multiplier=1.0):
    # True brown noise is a random walk (much softer than white noise)
    samples = int(SAMPLE_RATE * duration)
    white = np.random.normal(0, 1, samples)
    brown = np.cumsum(white) # This creates the deep, soft roar
    # Normalize to prevent distortion
    brown = brown / np.max(np.abs(brown))
    return (np.vstack((brown, brown)).T * (20000 * volume_multiplier)).astype(np.int16)

def gen_lush_pad(duration):
    # A warm, detuned ambient drone (Requires no melody)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # Base frequencies (Deep C and G)
    f1, f2, f3 = 130.81, 196.00, 65.41
    
    # Adding slight detuning (e.g., 130.81 and 131.5) creates a beautiful "chorus" or "breathing" effect
    layer1 = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * (f1 + 0.5) * t)
    layer2 = np.sin(2 * np.pi * f2 * t) + np.sin(2 * np.pi * (f2 - 0.3) * t)
    layer3 = np.sin(2 * np.pi * f3 * t) # Deep bass foundation
    
    pad = (layer1 * 0.4) + (layer2 * 0.3) + (layer3 * 0.5)
    pad = pad / np.max(np.abs(pad))
    return (np.vstack((pad, pad)).T * 18000).astype(np.int16)

print("1. Synthesizing Organic Sounds...")
wavfile.write("t_bin.wav", SAMPLE_RATE, gen_smooth_binaural(DUR))
wavfile.write("t_brown.wav", SAMPLE_RATE, gen_true_brown_noise(DUR))
wavfile.write("t_pad.wav", SAMPLE_RATE, gen_lush_pad(DUR))

print("2. Studio Mixing (Applying ultra-soft ADHD filters)...")
# Load into Pydub for precise EQ and Volume control

# 1. Binaural Tone: Very subtle, just enough for the brain to catch it
bin_layer = AudioSegment.from_wav("t_bin.wav") - 22

# 2. The Atmospheric Pad: This is the main melodic focus, kept warm and low
pad_layer = AudioSegment.from_wav("t_pad.wav").low_pass_filter(800) - 8

# 3. Soft Rainfall / Ocean: Using Brown noise, cutting the harsh highs, making it VERY quiet
rain_layer = AudioSegment.from_wav("t_brown.wav").low_pass_filter(1500).high_pass_filter(200) - 24

# 4. Deep Focus Brown Noise: Barely audible rumble for depth
depth_layer = AudioSegment.from_wav("t_brown.wav").low_pass_filter(150) - 26

# Mix the base layers
mix = pad_layer.overlay(rain_layer).overlay(depth_layer).overlay(bin_layer)

print("3. Adding Subtle Sky/Wind...")
# 5. Wind Texture: High-passed brown noise, very faint
wind_layer = AudioSegment.from_wav("t_brown.wav").high_pass_filter(1200) - 28
wind_layer = wind_layer.fade_in(5000)
mix = mix.overlay(wind_layer, position=120000) # Starts at 2:00 mark

print("4. Finalizing Master...")
mix.fade_out(4000).export("Janka_UltraSoft_Sample.mp3", format="mp3", bitrate="320k")

# Cleanup
for f in ["t_bin.wav", "t_brown.wav", "t_pad.wav"]: os.remove(f)
print("Ultra-Soft Sample complete!")
