import os
import numpy as np
from scipy.signal import sawtooth

# ==============================
# Audio Settings
# ==============================
SAMPLE_RATE = 44100        # Standard CD-quality sample rate
CHANNELS = 2               # Stereo output
DURATION_CHUNK = 5         # seconds per procedural audio chunk

# ==============================
# Presets Settings
# ==============================
REQUIRED_PRESET_KEYS = [
    "tempo", "scale", "instrument", "use_arpeggio",
    "reverb", "delay", "chorus", "phaser", "stereo_widen",
    "lowpass", "highpass"
]

# ==============================
# Default Instrument List
# ==============================
INSTRUMENTS = [
    'sine',
    'square',
    'triangle',
    'sawtooth',
    'fm_sine',
    'noise_pad'
]

# ==============================
# Musical Scales
# ==============================
# Each scale is a list of semitone intervals from the root
SCALES = {
    'major':      [0, 2, 4, 5, 7, 9, 11],
    'minor':      [0, 2, 3, 5, 7, 8, 10],
    'dorian':     [0, 2, 3, 5, 7, 9, 10],
    'phrygian':   [0, 1, 3, 5, 7, 8, 10],
    'lydian':     [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'locrian':    [0, 1, 3, 5, 6, 8, 10],
    'pentatonic_major': [0, 2, 4, 7, 9],
    'pentatonic_minor': [0, 3, 5, 7, 10]
}

# ==============================
# Musical Chords
# ==============================
CHORD_FORMULAS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8]
}

# ==============================
# Instruments
# ==============================
def sine_wave(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE*duration), endpoint=False)
    return np.sin(2*np.pi*freq*t)

def square_wave(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE*duration), endpoint=False)
    return np.sign(np.sin(2*np.pi*freq*t))

def triangle_wave(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE*duration), endpoint=False)
    return sawtooth(2*np.pi*freq*t, width=0.5)

def saw_wave(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE*duration), endpoint=False)
    return sawtooth(2*np.pi*freq*t)

def fm_sine(freq, duration, mod_index=2.0, mod_freq=2.0):
    t = np.linspace(0, duration, int(SAMPLE_RATE*duration), endpoint=False)
    return np.sin(2*np.pi*freq*t + mod_index*np.sin(2*np.pi*mod_freq*t))

def noise_pad(duration):
    return np.random.uniform(-0.3, 0.3, int(SAMPLE_RATE*duration))

INSTRUMENTS = {
    "sine": sine_wave,
    "square": square_wave,
    "triangle": triangle_wave,
    "sawtooth": saw_wave,
    "fm_sine": fm_sine,
    "noise_pad": noise_pad
}

# ==============================
# Folder Paths
# ==============================
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
PRESET_FOLDER = os.path.join(BASE_FOLDER, "presets")
EXPORT_FOLDER = os.path.join(BASE_FOLDER, "exports")
RESOURCES_FOLDER = os.path.join(BASE_FOLDER, "resources")

# Create folders if they do not exist
for folder in [PRESET_FOLDER, EXPORT_FOLDER, RESOURCES_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# ==============================
# Default FX Settings
# ==============================
DEFAULT_FX = {
    "reverb": {"enabled": True, "size": 0.4, "damping": 0.5, "mix": 0.3},
    "delay": {"enabled": True, "time": 0.3, "feedback": 0.35, "mix": 0.3},
    "chorus": {"enabled": True, "rate": 0.25, "depth": 0.3, "mix": 0.2},
    "phaser": {"enabled": True, "rate": 0.2, "depth": 0.3, "mix": 0.2},
    "stereo_widen": 0.0,
    "lowpass": 15000,
    "highpass": 20
}

# ==============================
# Default LFO Settings
# ==============================
DEFAULT_LFO = {
    "global": {
        "tempo": {"rate": 0.005, "amplitude": 20},
        "reverb": {"rate": 0.002, "amplitude": 0.5},
        "delay": {"rate": 0.002, "amplitude": 0.5},
        "chorus": {"rate": 0.001, "amplitude": 0.5},
        "phaser": {"rate": 0.001, "amplitude": 0.5},
        "stereo": {"rate": 0.001, "amplitude": 0.5},
    },
    "layer": [
        {"volume": {"rate": 0.001, "amplitude": 0.3},
         "pan": {"rate": 0.0005, "amplitude": 0.5},
         "timbre": {"rate": 0.0007, "amplitude": 0.5}},
        {"volume": {"rate": 0.002, "amplitude": 0.3},
         "pan": {"rate": 0.001, "amplitude": 0.5},
         "timbre": {"rate": 0.001, "amplitude": 0.5}},
        {"volume": {"rate": 0.003, "amplitude": 0.3},
         "pan": {"rate": 0.0015, "amplitude": 0.5},
         "timbre": {"rate": 0.0015, "amplitude": 0.5}},
        {"volume": {"rate": 0.004, "amplitude": 0.3},
         "pan": {"rate": 0.002, "amplitude": 0.5},
         "timbre": {"rate": 0.002, "amplitude": 0.5}}
    ]
}

# ==============================
# Other Defaults
# ==============================
DEFAULT_TEMPO = 60             # BPM
DEFAULT_SCENE_DURATION = 30    # seconds
DEFAULT_SESSION_DURATION = 180 # seconds
