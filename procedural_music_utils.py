# procedural_music_utils.py
from typing import List, Optional
from utils import RandomContext, random_distribute, random_boolean_list, weighted_random_list, unique_weighted_random_list, random_pattern_from_weights, shuffle_list, clamp

# ==============================
# Musical Constants
# ==============================
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "chromatic": list(range(12))
}

DYNAMICS = {
    "pp": 32,
    "p": 48,
    "mp": 64,
    "mf": 80,
    "f": 96,
    "ff": 112
}

RHYTHM_TYPES = ["whole", "half", "quarter", "eighth", "sixteenth"]

CHORD_TYPES = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7]
}

# ==============================
# Humanization Parameters
# ==============================
HUMANIZATION = {
    "timing_jitter": 0.02,   # ±2% timing variation
    "velocity_jitter": 0.05, # ±5% velocity variation
    "swing_strength": 0.15   # swing feel for offbeats
}

# ==============================
# Scale / Note Utilities
# ==============================
def scale_notes(root: str, scale_name: str, octaves: int = 1) -> List[str]:
    """Return note names for the given scale starting at root across octaves."""
    root_idx = NOTE_NAMES.index(root)
    scale_intervals = SCALES.get(scale_name, SCALES['major'])
    notes = []
    for o in range(octaves):
        for interval in scale_intervals:
            note_idx = (root_idx + interval + 12 * o) % 12
            octave = o + 4  # default middle octave
            notes.append(f"{NOTE_NAMES[note_idx]}{octave}")
    return notes

def random_note_from_scale(scale_notes_list: List[str], rc: Optional[RandomContext] = None) -> str:
    return weighted_random_list(scale_notes_list, count=1, rc=rc)[0]

# ==============================
# Rhythm Utilities
# ==============================
def random_rhythm_pattern(length: int, rc: Optional[RandomContext] = None) -> List[str]:
    """Generate a rhythm pattern as a list of note types."""
    return random_pattern_from_weights(length, RHYTHM_TYPES, rc=rc)

def apply_swing(rhythm_pattern: List[str], rc: Optional[RandomContext] = None) -> List[float]:
    """
    Convert rhythm types into durations with swing applied.
    Returns a list of floats representing beat lengths (1.0 = quarter note).
    """
    duration_map = {"whole": 4.0, "half": 2.0, "quarter": 1.0, "eighth": 0.5, "sixteenth": 0.25}
    rc_local = rc.random if rc else None

    durations = []
    for i, note_type in enumerate(rhythm_pattern):
        dur = duration_map.get(note_type, 1.0)
        # Apply swing on every other note
        if i % 2 == 1:
            dur *= 1.0 + HUMANIZATION["swing_strength"]
        # Apply optional small timing jitter
        if rc_local:
            dur *= 1.0 + rc_local.uniform(-HUMANIZATION["timing_jitter"], HUMANIZATION["timing_jitter"])
        durations.append(dur)
    return durations

def random_velocity_pattern(length: int, min_vel: int = 48, max_vel: int = 100, rc: Optional[RandomContext] = None) -> List[int]:
    """Generate a list of velocities for a sequence of notes."""
    return [int(clamp(v, min_vel, max_vel)) for v in random_distribute(total=(min_vel+max_vel)*length/2, parts=length, min_val=min_vel, max_val=max_vel, rc=rc)]

def humanize_velocities(velocities: List[int], rc: Optional[RandomContext] = None) -> List[int]:
    """Slightly randomize velocities to avoid robotic feel."""
    rc_local = rc.random if rc else None
    humanized = []
    for v in velocities:
        jitter = 1.0
        if rc_local:
            jitter += rc_local.uniform(-HUMANIZATION["velocity_jitter"], HUMANIZATION["velocity_jitter"])
        humanized.append(int(clamp(v * jitter, 1, 127)))
    return humanized

def random_boolean_rhythm(length: int, probability: float = 0.5, rc: Optional[RandomContext] = None) -> List[bool]:
    return random_boolean_list(length, p=probability, rc=rc)

# ==============================
# Chord Utilities
# ==============================
def generate_chord(root: str, chord_type: str, oct: int = 4) -> List[str]:
    """Return note names for a chord based on root and type."""
    root_idx = NOTE_NAMES.index(root)
    intervals = CHORD_TYPES.get(chord_type, CHORD_TYPES['major'])
    chord_notes = []
    for interval in intervals:
        note_idx = (root_idx + interval) % 12
        chord_notes.append(f"{NOTE_NAMES[note_idx]}{oct}")
    return chord_notes

def random_chord_progression(roots: List[str], chord_types: Optional[List[str]] = None, length: int = 4, rc: Optional[RandomContext] = None) -> List[List[str]]:
    """Generate a random chord progression."""
    chord_types = chord_types or list(CHORD_TYPES.keys())
    progression = []
    for _ in range(length):
        root = weighted_random_list(roots, count=1, rc=rc)[0]
        chord_type = weighted_random_list(chord_types, count=1, rc=rc)[0]
        progression.append(generate_chord(root, chord_type))
    return progression

def arpeggiate_chord(chord: List[str], pattern_length: int, rc: Optional[RandomContext] = None) -> List[str]:
    """Generate an arpeggio pattern from a chord over given length."""
    return [weighted_random_list(chord, count=1, rc=rc)[0] for _ in range(pattern_length)]

# ==============================
# Advanced Features
# ==============================
def probabilistic_note_variation(notes: List[str], scale_notes_list: List[str], variation_prob: float = 0.2, rc: Optional[RandomContext] = None) -> List[str]:
    """Randomly swap some notes with another note from the scale based on probability."""
    rc_local = rc.random if rc else None
    output = []
    for note in notes:
        if rc_local and rc_local.random() < variation_prob:
            new_note = weighted_random_list(scale_notes_list, count=1, rc=rc)[0]
            output.append(new_note)
        else:
            output.append(note)
    return output

def weighted_chord_progression(chord_progression: List[List[str]], transition_weights: Optional[List[float]] = None, rc: Optional[RandomContext] = None) -> List[List[str]]:
    """Apply weighted selection between chords for smoother progressions."""
    if not chord_progression:
        return []
    rc_local = rc.random if rc else None
    output = [chord_progression[0]]
    for i in range(1, len(chord_progression)):
        weights = transition_weights if transition_weights else None
        next_chord = weighted_random_list(chord_progression[i:], weights=weights, count=1, rc=rc)[0]
        output.append(next_chord)
    return output