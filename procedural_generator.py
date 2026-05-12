# procedural_generator.py
import numpy as np
import random
from audio_utils import generate_tone, apply_pan
from lfo import LayerLFO
import config

SAMPLE_RATE = config.SAMPLE_RATE

# ==============================
# Musical Scales
# ==============================
SCALES = config.SCALES

# ==============================
# Chord Formulas
# ==============================
CHORD_FORMULAS = config.CHORD_FORMULAS

# ==============================
# MIDI to Frequency
# ==============================
def note_to_freq(note: int):
    return 440 * 2 ** ((note - 69) / 12)

# ==============================
# Chord Generation
# ==============================
def generate_chord(root_note: int, chord_type="minor", inversion=None):
    intervals = CHORD_FORMULAS.get(chord_type, [0, 4, 7])
    notes = [root_note + i for i in intervals]
    if inversion:
        for _ in range(inversion):
            note = notes.pop(0)
            notes.append(note + 12)
    return notes

# ==============================
# Melody Generation
# ==============================
def generate_melody(scale_name="minor", length=8, base_note=60):
    scale = SCALES.get(scale_name, SCALES["minor"])
    melody = []
    for _ in range(length):
        step = random.choice(scale)
        octave_shift = 12 * random.randint(0,1)
        melody.append(base_note + step + octave_shift)
    return melody

# ==============================
# Multi-layer Procedural Chunk
# ==============================
def generate_procedural_chunk(duration_sec, tempo=60, scale="minor",
                              instrument="sine", use_arpeggio=True,
                              return_layers=False):
    """
    Generate 4 layers: drone, chords, melody, noise
    Returns either mixed stereo audio or a list of stereo layers
    """
    total_samples = int(duration_sec * config.SAMPLE_RATE)
    layers = []

    # Initialize LFOs for layers
    layer_lfos = [LayerLFO() for _ in range(4)]

    # --- Layer 0: Drone ---
    drone_note = 48 + random.randint(0, 12)
    drone_wave = generate_tone(note_to_freq(drone_note), duration_sec, instrument)
    pan_val = layer_lfos[0].step(1/config.SAMPLE_RATE)["pan"]
    layers.append(apply_pan(drone_wave, pan_val))

    # --- Layer 1: Chords ---
    root_note = 60
    chord_notes = generate_chord(root_note, chord_type=random.choice(["minor","major","sus2"]))
    chord_layer = np.zeros((total_samples,))
    for note in chord_notes:
        chord_layer += generate_tone(note_to_freq(note), duration_sec, instrument)
    chord_layer /= max(len(chord_notes), 1)
    pan_val = layer_lfos[1].step(1/config.SAMPLE_RATE)["pan"]
    layers.append(apply_pan(chord_layer, pan_val))

    # --- Layer 2: Melody / Arpeggio ---
    melody_notes = generate_melody(scale_name=scale, length=int(duration_sec * tempo / 60))
    melody_layer = np.zeros((total_samples,))
    for idx, note in enumerate(melody_notes):
        note_dur = duration_sec / max(len(melody_notes),1)
        start_idx = int(idx * note_dur * config.SAMPLE_RATE)
        end_idx = start_idx + int(note_dur * config.SAMPLE_RATE)
        end_idx = min(end_idx, total_samples)
        melody_wave = generate_tone(note_to_freq(note), note_dur, instrument)
        melody_layer[start_idx:end_idx] += melody_wave[:end_idx-start_idx]
    pan_val = layer_lfos[2].step(1/config.SAMPLE_RATE)["pan"]
    layers.append(apply_pan(melody_layer, pan_val))

    # --- Layer 3: Noise / Texture ---
    noise_wave = generate_tone(0, duration_sec, instrument="noise_pad")
    pan_val = layer_lfos[3].step(1/config.SAMPLE_RATE)["pan"]
    layers.append(apply_pan(noise_wave, pan_val))

    # Return layers or mixed
    if return_layers:
        return layers
    mixed = np.sum(layers, axis=0)
    return np.clip(mixed, -1, 1)