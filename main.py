import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import os

# --- CONFIGURATION ---
SAMPLE_RATE = 44100
CARRIER_FREQ = 200  # A comfortable base frequency for binaural beats
TOTAL_DURATION = 1986  # 33 mins 6 seconds

def generate_binaural_channel(duration, beat_freq, carrier):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    left_channel = np.sin(2 * np.pi * (carrier - beat_freq / 2) * t)
    right_channel = np.sin(2 * np.pi * (carrier + beat_freq / 2) * t)
    
    # Convert to 16-bit PCM
    audio_data = np.vstack((left_channel, right_channel)).T
    return (audio_data * 32767).astype(np.int16)

def generate_brown_noise(duration):
    """Creates a soft, rain-like texture using Brown Noise"""
    samples = int(SAMPLE_RATE * duration)
    unevenness = np.random.uniform(-1, 1, samples)
    brown_noise = np.cumsum(unevenness)
    # Normalize
    brown_noise /= np.max(np.abs(brown_noise))
    # Stereo
    stereo_brown = np.vstack((brown_noise, brown_noise)).T
    return (stereo_brown * 15000).astype(np.int16)

def generate_drone_pad(duration, freq=100):
    """Creates a soft atmospheric space pad using a low sine drone"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    # Multi-layered sine waves for a 'pad' feel
    tone = (np.sin(2 * np.pi * freq * t) + 
            0.5 * np.sin(2 * np.pi * (freq * 1.5) * t) +
            0.2 * np.sin(2 * np.pi * (freq * 0.5) * t))
    tone /= np.max(np.abs(tone))
    stereo_tone = np.vstack((tone, tone)).T
    return (stereo_tone * 8000).astype(np.int16)

print("Step 1: Generating Binaural Segments...")
# Segment 1: 6 mins (360s) @ 10Hz
seg1 = generate_binaural_channel(360, 10, CARRIER_FREQ)
# Segment 2: 20 mins (1200s) @ 12Hz
seg2 = generate_binaural_channel(1200, 12, CARRIER_FREQ)
# Segment 3: 7 mins 6s (426s) @ 14Hz
seg3 = generate_binaural_channel(426, 14, CARRIER_FREQ)

full_binaural_data = np.concatenate((seg1, seg2, seg3), axis=0)
wavfile.write("temp_binaural.wav", SAMPLE_RATE, full_binaural_data)

print("Step 2: Generating Atmospheric Textures (Rain & Space)...")
rain_data = generate_brown_noise(TOTAL_DURATION)
wavfile.write("temp_rain.wav", SAMPLE_RATE, rain_data)

space_data = generate_drone_pad(TOTAL_DURATION)
wavfile.write("temp_space.wav", SAMPLE_RATE, space_data)

print("Step 3: Mixing and Applying ADHD focus filters...")
# Load into Pydub
binaural = AudioSegment.from_wav("temp_binaural.wav") - 18  # Low volume
rain = AudioSegment.from_wav("temp_rain.wav") - 10        # Soft rain
space = AudioSegment.from_wav("temp_space.wav") - 15       # Deep pad

# Initial Mix
mix = rain.overlay(space).overlay(binaural)

print("Step 4: Adding Sky/Wind texture to final 90 seconds...")
# Create a rushing wind effect for the end
wind_duration = 90
wind_raw = generate_brown_noise(wind_duration)
wavfile.write("temp_wind.wav", SAMPLE_RATE, wind_raw)
wind = AudioSegment.from_wav("temp_wind.wav").low_pass_filter(1500) - 12
wind = wind.fade_in(5000) # Subtle entrance

# Overlay wind at the 1896 second mark (TOTAL_DURATION - 90)
mix = mix.overlay(wind, position=(TOTAL_DURATION - 90) * 1000)

print("Step 5: Finalizing (Fade out and Exporting)...")
final_audio = mix.fade_out(5000) # 5 second smooth ending

# Export both versions
final_audio.export("Janka_ADHD_Creative_Flow.wav", format="wav")
final_audio.export("Janka_ADHD_Creative_Flow.mp3", format="mp3", bitrate="320k")

# Cleanup temp files
for f in ["temp_binaural.wav", "temp_rain.wav", "temp_space.wav", "temp_wind.wav"]:
    os.remove(f)

print("SUCCESS! Files created: Janka_ADHD_Creative_Flow.wav & .mp3")
