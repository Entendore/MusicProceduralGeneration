# procedural_generator.py
import numpy as np
from scipy.signal import sawtooth
import random

SAMPLE_RATE = 44100

# ==============================
# Musical Scales
# ==============================
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10]
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
# Note to Frequency
# ==============================
def note_to_freq(note: int, base_freq=440):
    """
    Convert MIDI note number to frequency in Hz.
    note: MIDI number (e.g., 69 = A4)
    """
    return base_freq * 2 ** ((note - 69) / 12)

# ==============================
# Procedural Chord / Arpeggio Generation
# ==============================
CHORD_FORMULAS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8]
}

def generate_chord(root_note: int, chord_type="minor", inversion=None):
    intervals = CHORD_FORMULAS.get(chord_type, [0, 4, 7])
    notes = [(root_note + i) for i in intervals]
    if inversion:
        for _ in range(inversion):
            note = notes.pop(0)
            notes.append(note + 12)
    return notes

def generate_melody(scale_name="minor", length=8, base_note=60):
    scale = SCALES.get(scale_name, SCALES["minor"])
    melody = []
    for _ in range(length):
        step = random.choice(scale)
        octave_shift = 12 * random.randint(0,1)
        melody.append(base_note + step + octave_shift)
    return melody

# ==============================
# Multi-layer Procedural Chunk Generator
# ==============================
def generate_procedural_chunk(duration_sec, tempo=60, scale="minor", instrument="sine",
                              use_arpeggio=True, return_layers=False):
    """
    Generate multiple layers for procedural music chunk.
    Returns either a mixed stereo audio or list of layers.
    Each layer: Nx2 stereo numpy array
    """
    num_layers = 4  # drone, chords, melody, noise
    layers = []

    # --- Time grid ---
    total_samples = int(duration_sec * SAMPLE_RATE)
    t = np.linspace(0, duration_sec, total_samples, endpoint=False)

    # --- Base Layer: Drone ---
    drone_note = 48 + random.randint(0,12)
    drone_wave = INSTRUMENTS.get(instrument, sine_wave)(note_to_freq(drone_note), duration_sec)
    layers.append(np.stack([drone_wave, drone_wave], axis=1))

    # --- Layer 1: Chords ---
    root_note = 60
    chord_notes = generate_chord(root_note, chord_type=random.choice(["minor","major","sus2"]))
    chord_layer = np.zeros((total_samples,))
    for note in chord_notes:
        chord_layer += INSTRUMENTS.get(instrument, sine_wave)(note_to_freq(note), duration_sec)
    chord_layer /= max(len(chord_notes), 1)
    layers.append(np.stack([chord_layer, chord_layer], axis=1))

    # --- Layer 2: Melody / Arpeggio ---
    melody_notes = generate_melody(scale_name=scale, length=int(duration_sec * tempo / 60))
    melody_layer = np.zeros((total_samples,))
    for note in melody_notes:
        note_dur = duration_sec / max(len(melody_notes),1)
        start_idx = int(melody_notes.index(note) * note_dur * SAMPLE_RATE)
        end_idx = start_idx + int(note_dur * SAMPLE_RATE)
        end_idx = min(end_idx, total_samples)
        melody_wave = INSTRUMENTS.get(instrument, sine_wave)(note_to_freq(note), note_dur)
        melody_layer[start_idx:end_idx] += melody_wave[:end_idx-start_idx]
    layers.append(np.stack([melody_layer, melody_layer], axis=1))

    # --- Layer 3: Noise / Texture ---
    noise_wave = noise_pad(duration_sec)
    layers.append(np.stack([noise_wave, noise_wave], axis=1))

    if return_layers:
        return layers
    else:
        mixed = np.sum(layers, axis=0)
        mixed = np.clip(mixed, -1, 1)
        return mixed
