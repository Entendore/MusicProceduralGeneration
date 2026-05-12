# fx_chain.py
import numpy as np
from scipy.signal import butter, lfilter

class FXChain:
    """
    Modular FX chain for procedural audio.
    Supports reverb, delay, chorus, phaser, stereo widening, and filters.
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

        # FX Parameters
        self.reverb_amount = 0.3
        self.delay_amount = 0.3
        self.chorus_amount = 0.0
        self.phaser_amount = 0.0
        self.stereo_widen = 0.0
        self.lowpass_cutoff = 20000
        self.highpass_cutoff = 20

    # ==============================
    # Parameter setters
    # ==============================
    def set_reverb(self, value: float): self.reverb_amount = np.clip(value, 0, 1)
    def set_delay(self, value: float): self.delay_amount = np.clip(value, 0, 1)
    def set_chorus(self, value: float): self.chorus_amount = np.clip(value, 0, 1)
    def set_phaser(self, value: float): self.phaser_amount = np.clip(value, 0, 1)
    def set_stereo_widen(self, value: float): self.stereo_widen = np.clip(value, 0, 1)
    def set_lowpass(self, freq: float): self.lowpass_cutoff = np.clip(freq, 20, self.sample_rate/2)
    def set_highpass(self, freq: float): self.highpass_cutoff = np.clip(freq, 20, self.sample_rate/2)

    # ==============================
    # Apply FX chain
    # ==============================
    def apply(self, audio: np.ndarray) -> np.ndarray:
        if audio.ndim == 1:
            audio = np.stack([audio, audio], axis=1)
        processed = audio.copy()

        if self.reverb_amount > 0:
            processed = self._apply_reverb(processed, self.reverb_amount)
        if self.delay_amount > 0:
            processed = self._apply_delay(processed, self.delay_amount)
        if self.chorus_amount > 0:
            processed = self._apply_chorus(processed, self.chorus_amount)
        if self.phaser_amount > 0:
            processed = self._apply_phaser(processed, self.phaser_amount)
        if self.stereo_widen > 0:
            processed = self._apply_stereo_widen(processed, self.stereo_widen)

        processed = self._apply_filters(processed)
        return np.clip(processed, -1.0, 1.0)

    # ==============================
    # Internal FX Implementations
    # ==============================
    def _apply_reverb(self, audio, amount):
        delay_samples = int(0.03 * self.sample_rate)
        wet = np.zeros_like(audio)
        for ch in range(2):
            wet_ch = np.zeros_like(audio[:, ch])
            for i in range(delay_samples, len(audio)):
                wet_ch[i] = audio[i, ch] + amount * wet_ch[i - delay_samples]
            wet[:, ch] = wet_ch
        return (1 - amount) * audio + amount * wet

    def _apply_delay(self, audio, amount):
        delay_samples = int(0.25 * self.sample_rate)
        wet = np.zeros_like(audio)
        for ch in range(2):
            wet_ch = np.zeros_like(audio[:, ch])
            for i in range(delay_samples, len(audio)):
                wet_ch[i] = audio[i, ch] + 0.5 * amount * audio[i - delay_samples, ch]
            wet[:, ch] = wet_ch
        return (1 - amount) * audio + amount * wet

    def _apply_chorus(self, audio, amount):
        n_samples = audio.shape[0]
        output = audio.copy()
        delay_samples = int(0.003 * self.sample_rate)
        rate = 0.25 * amount
        for ch in range(2):
            for i in range(delay_samples, n_samples):
                mod = int(delay_samples * np.sin(2 * np.pi * rate * i / self.sample_rate))
                output[i, ch] += 0.5 * audio[i - mod, ch]
        return output

    def _apply_phaser(self, audio, amount):
        n_samples = audio.shape[0]
        output = audio.copy()
        rate = 0.2 * amount
        depth = 0.02 * amount
        for ch in range(2):
            for i in range(n_samples):
                shift = int(depth * self.sample_rate * np.sin(2 * np.pi * rate * i / self.sample_rate))
                if i - shift >= 0:
                    output[i, ch] += audio[i - shift, ch]
        return output

    def _apply_stereo_widen(self, audio, amount):
        mid = np.mean(audio, axis=1, keepdims=True)
        side = (audio[:, 0:1] - audio[:, 1:2]) * (1 + amount)
        audio[:, 0] = mid[:, 0] + side[:, 0]
        audio[:, 1] = mid[:, 0] - side[:, 0]
        return audio

    def _apply_filters(self, audio):
        filtered = np.zeros_like(audio)
        for ch in range(2):
            x = audio[:, ch]
            if self.highpass_cutoff > 20:
                b, a = butter(2, self.highpass_cutoff / (0.5 * self.sample_rate), btype='high')
                x = lfilter(b, a, x)
            if self.lowpass_cutoff < self.sample_rate / 2:
                b, a = butter(2, self.lowpass_cutoff / (0.5 * self.sample_rate), btype='low')
                x = lfilter(b, a, x)
            filtered[:, ch] = x
        return filtered