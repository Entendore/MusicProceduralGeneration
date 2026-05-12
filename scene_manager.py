# scene_manager.py
import random
from presets import random_preset

class SceneManager:
    def __init__(self, scales, instruments, evolve=True):
        self.scales = scales
        self.instruments = instruments
        self.evolve = evolve
        self.current_scene = random_preset(scales, instruments)
        self.scene_history = [self.current_scene.copy()]
        self.scene_future = []

    def next_scene(self):
        """Move to the next procedural scene (randomized)."""
        if self.scene_future:
            self.current_scene = self.scene_future.pop(0)
        else:
            self.current_scene = random_preset(self.scales, self.instruments)
        
        self.scene_history.append(self.current_scene.copy())
        return self.current_scene

    def previous_scene(self):
        """Revert to the previous scene."""
        if len(self.scene_history) > 1:
            self.scene_future.insert(0, self.current_scene)
            self.scene_history.pop()
            self.current_scene = self.scene_history[-1].copy()
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

    def generate_scene_preview(self, count=5):
        """Generate preview of upcoming scenes."""
        preview = []
        for _ in range(count):
            preview.append(random_preset(self.scales, self.instruments))
        return preview

    def get_scene_timeline(self):
        """Get the timeline of past, current and future scenes."""
        return {
            "past": self.scene_history[:-1],
            "current": self.current_scene,
            "future": self.scene_future
        }