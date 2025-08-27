# config.py
import os

# ==============================
# Audio Settings
# ==============================
SAMPLE_RATE = 44100        # Standard CD-quality sample rate
CHANNELS = 2               # Stereo output
DURATION_CHUNK = 5         # seconds per procedural audio chunk

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
# Folder Paths
# ==============================
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
PRESET_FOLDER = os.path.join(BASE_FOLDER, "presets")
EXPORT_FOLDER = os.path.join(BASE_FOLDER, "exports")
RESOURCES_FOLDER = os.path.join(BASE_FOLDER, "resources")

# ==============================
# Default FX Settings
# ==============================
DEFAULT_FX = {
    "reverb": {
        "enabled": True,
        "size": 0.4,
        "damping": 0.5,
        "mix": 0.3
    },
    "delay": {
        "enabled": True,
        "time": 0.3,
        "feedback": 0.35,
        "mix": 0.3
    },
    "chorus": {
        "enabled": True,
        "rate": 0.25,
        "depth": 0.3,
        "mix": 0.2
    },
    "phaser": {
        "enabled": True,
        "rate": 0.2,
        "depth": 0.3,
        "mix": 0.2
    },
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
        {   # Layer 0 - Drone
            "volume": {"rate": 0.001, "amplitude": 0.3},
            "pan": {"rate": 0.0005, "amplitude": 0.5},
            "timbre": {"rate": 0.0007, "amplitude": 0.5}
        },
        {   # Layer 1 - Chords
            "volume": {"rate": 0.002, "amplitude": 0.3},
            "pan": {"rate": 0.001, "amplitude": 0.5},
            "timbre": {"rate": 0.001, "amplitude": 0.5}
        },
        {   # Layer 2 - Melody
            "volume": {"rate": 0.003, "amplitude": 0.3},
            "pan": {"rate": 0.0015, "amplitude": 0.5},
            "timbre": {"rate": 0.0015, "amplitude": 0.5}
        },
        {   # Layer 3 - Noise / FX
            "volume": {"rate": 0.004, "amplitude": 0.3},
            "pan": {"rate": 0.002, "amplitude": 0.5},
            "timbre": {"rate": 0.002, "amplitude": 0.5}
        }
    ]
}

# ==============================
# Other Defaults
# ==============================
DEFAULT_TEMPO = 60            # BPM
DEFAULT_SCENE_DURATION = 30   # seconds
DEFAULT_SESSION_DURATION = 180 # seconds
