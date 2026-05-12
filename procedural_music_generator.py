# procedural_music_generator.py
from typing import List, Optional
from utils import RandomContext
from procedural_music_utils import (
    scale_notes,
    random_note_from_scale,
    random_rhythm_pattern,
    apply_swing,
    random_velocity_pattern,
    humanize_velocities,
    probabilistic_note_variation,
    random_chord_progression,
    arpeggiate_chord,
    weighted_chord_progression
)

class ProceduralMusicGenerator:
    def __init__(
        self,
        root: str = "C",
        scale_name: str = "major",
        octaves: int = 1,
        seed: Optional[int] = None
    ):
        self.rc = RandomContext(seed)
        self.root = root
        self.scale_name = scale_name
        self.octaves = octaves
        self.scale = scale_notes(root, scale_name, octaves)

    def generate_melody(
        self,
        length: int = 16,
        variation_prob: float = 0.2
    ) -> List[str]:
        """Generate a melody sequence with probabilistic variation."""
        melody = [random_note_from_scale(self.scale, rc=self.rc) for _ in range(length)]
        melody = probabilistic_note_variation(melody, self.scale, variation_prob, rc=self.rc)
        return melody

    def generate_rhythm(
        self,
        length: int = 16,
        swing: bool = True
    ) -> List[float]:
        """Generate rhythm durations with optional swing."""
        rhythm = random_rhythm_pattern(length, rc=self.rc)
        if swing:
            return apply_swing(rhythm, rc=self.rc)
        return [1.0 if r=="quarter" else 0.5 for r in rhythm]  # default simplification

    def generate_velocities(
        self,
        length: int = 16,
        min_vel: int = 48,
        max_vel: int = 100
    ) -> List[int]:
        """Generate a humanized velocity sequence."""
        velocities = random_velocity_pattern(length, min_vel, max_vel, rc=self.rc)
        velocities = humanize_velocities(velocities, rc=self.rc)
        return velocities

    def generate_chords(
        self,
        roots: List[str],
        length: int = 4
    ) -> List[List[str]]:
        """Generate a weighted chord progression."""
        chords = random_chord_progression(roots, length=length, rc=self.rc)
        return weighted_chord_progression(chords, rc=self.rc)

    def generate_arpeggio(
        self,
        chord: List[str],
        pattern_length: int = 8
    ) -> List[str]:
        """Generate an arpeggio sequence from a chord."""
        return arpeggiate_chord(chord, pattern_length, rc=self.rc)

    def generate_full_track(
        self,
        melody_length: int = 16,
        chord_roots: Optional[List[str]] = None,
        swing: bool = True
    ):
        """Generate a full track with melody, rhythm, velocities, chords, and arpeggios."""
        melody = self.generate_melody(melody_length)
        rhythm = self.generate_rhythm(melody_length, swing=swing)
        velocities = self.generate_velocities(melody_length)
        chord_roots = chord_roots or [self.root]
        chords = self.generate_chords(chord_roots, length=melody_length // 4)
        arpeggios = []
        for chord in chords:
            arp = self.generate_arpeggio(chord, pattern_length=melody_length // len(chords))
            arpeggios.extend(arp)
        return {
            "melody": melody,
            "rhythm": rhythm,
            "velocities": velocities,
            "chords": chords,
            "arpeggios": arpeggios
        }