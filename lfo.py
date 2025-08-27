import math
import random

class LFO:
    def __init__(self, rate=0.001, amplitude=1.0, waveform="sine", phase=None):
        self.rate = rate
        self.amplitude = amplitude
        self.waveform = waveform
        self.phase = phase if phase is not None else random.uniform(0, 2 * math.pi)
        self.time = 0.0

    def step(self, dt: float) -> float:
        self.time += dt
        t = 2 * math.pi * self.rate * self.time + self.phase
        if self.waveform == "sine":
            value = math.sin(t)
        elif self.waveform == "square":
            value = 1.0 if math.sin(t) >= 0 else -1.0
        elif self.waveform == "triangle":
            value = 2 * abs(2 * ((self.rate * self.time + self.phase/(2*math.pi)) % 1) - 1) - 1
        elif self.waveform == "sawtooth":
            value = 2 * ((self.rate * self.time + self.phase/(2*math.pi)) % 1) - 1
        else:
            value = math.sin(t)
        return value * self.amplitude

    def reset(self):
        self.time = 0.0
        self.phase = random.uniform(0, 2 * math.pi)


class LayerLFO:
    def __init__(self, volume=None, pan=None, timbre=None):
        self.volume = volume if volume else LFO(rate=0.001, amplitude=0.3, waveform="sine")
        self.pan = pan if pan else LFO(rate=0.001, amplitude=0.5, waveform="triangle")
        self.timbre = timbre if timbre else LFO(rate=0.001, amplitude=0.5, waveform="sawtooth")

    def step(self, dt: float) -> dict:
        return {
            "volume": self.volume.step(dt),
            "pan": self.pan.step(dt),
            "timbre": self.timbre.step(dt)
        }

    def reset(self):
        self.volume.reset()
        self.pan.reset()
        self.timbre.reset()
