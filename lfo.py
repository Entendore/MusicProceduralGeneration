# lfo.py
import math
import random

class LFO:
    """
    Low-Frequency Oscillator for evolving parameters.
    Supports sine wave modulation.
    """
    def __init__(self, rate=0.001, amplitude=1.0, phase=None):
        """
        rate: LFO speed (cycles per second)
        amplitude: modulation depth
        phase: initial phase in radians
        """
        self.rate = rate
        self.amplitude = amplitude
        self.phase = phase if phase is not None else random.uniform(0, 2 * math.pi)
        self.time = 0.0

    def step(self, dt: float) -> float:
        """
        Advance LFO by dt seconds and return modulation value (-amplitude to +amplitude)
        """
        self.time += dt
        value = math.sin(2 * math.pi * self.rate * self.time + self.phase) * self.amplitude
        return value

    def reset(self):
        self.time = 0.0
        self.phase = random.uniform(0, 2 * math.pi)


class LayerLFO:
    """
    Container for per-layer LFOs controlling volume, pan, timbre, etc.
    """
    def __init__(self, volume=None, pan=None, timbre=None):
        self.volume = volume if volume else LFO(rate=0.001, amplitude=0.3)
        self.pan = pan if pan else LFO(rate=0.001, amplitude=0.5)
        self.timbre = timbre if timbre else LFO(rate=0.001, amplitude=0.5)

    def step(self, dt: float) -> dict:
        """
        Advance all LFOs by dt seconds and return their current values.
        Returns:
            dict with keys 'volume', 'pan', 'timbre'
        """
        return {
            "volume": self.volume.step(dt),
            "pan": self.pan.step(dt),
            "timbre": self.timbre.step(dt)
        }

    def reset(self):
        self.volume.reset()
        self.pan.reset()
        self.timbre.reset()
