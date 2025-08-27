import random
from presets import random_preset

class SceneManager:
    def __init__(self, scales, instruments, evolve=True):
        self.scales = scales
        self.instruments = instruments
        self.evolve = evolve
        self.current_scene = random_preset(scales, instruments)

    def next_scene(self):
        """Move to the next procedural scene (randomized)."""
        self.current_scene = random_preset(self.scales, self.instruments)
        return self.current_scene

    def evolve_scene(self):
        """Apply small changes to keep music evolving."""
        if not self.evolve:
            return self.current_scene

        new_scene = self.current_scene.copy()
        change_key = random.choice(list(new_scene.keys()))

        if isinstance(new_scene[change_key], int):
            jitter = random.randint(-5, 5)
            new_scene[change_key] = max(0, new_scene[change_key] + jitter)
        elif isinstance(new_scene[change_key], str):
            # maybe change instrument/scale slightly
            if change_key == "scale":
                new_scene[change_key] = random.choice(list(self.scales.keys()))
            elif change_key == "instrument":
                new_scene[change_key] = random.choice(self.instruments)

        self.current_scene = new_scene
        return new_scene
