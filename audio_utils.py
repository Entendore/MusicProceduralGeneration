import numpy as np
from fx_chain import FXChain
from scipy.signal import lfilter
import config

SAMPLE_RATE = config.SAMPLE_RATE

# ------------------------------
# Stereo Panning
# ------------------------------
def apply_pan(signal: np.ndarray, pan: float) -> np.ndarray:
    pan = np.clip(pan, -1, 1)
    left = signal * np.sqrt(0.5 * (1 - pan))
    right = signal * np.sqrt(0.5 * (1 + pan))
    return np.stack([left, right], axis=1)

# ------------------------------
# Envelopes
# ------------------------------
def apply_envelope(signal: np.ndarray, attack=0.1, decay=0.5):
    n = len(signal)
    env = np.ones(n)
    attack_samples = int(attack * n)
    decay_samples = int(decay * n)
    if attack_samples > 0:
        env[:attack_samples] = np.linspace(0, 1, attack_samples)
    if decay_samples > 0:
        env[-decay_samples:] = np.linspace(1, 0, decay_samples)
    return signal * env

# ------------------------------
# Tone Generators
# ------------------------------
def midi_to_freq(midi_note: int) -> float:
    return 440 * 2 ** ((midi_note - 69) / 12)

def generate_tone(frequency, duration, instrument='sine', volume=0.2):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    if instrument == 'sine':
        wave = np.sin(2 * np.pi * frequency * t)
    elif instrument == 'square':
        wave = np.sign(np.sin(2 * np.pi * frequency * t))
    elif instrument == 'triangle':
        wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
    elif instrument == 'sawtooth':
        wave = 2 * (t * frequency - np.floor(0.5 + t * frequency))
    elif instrument == 'fm_sine':
        mod_freq = frequency * 2
        mod_index = 2.0
        wave = np.sin(2 * np.pi * frequency * t + mod_index * np.sin(2 * np.pi * mod_freq * t))
    elif instrument == 'noise_pad':
        wave = np.random.normal(0, 1, len(t)).astype(np.float32)
        wave = apply_envelope(wave, attack=0.5, decay=0.7)
    return (wave * volume).astype(np.float32)

def generate_noise(duration, volume=0.05):
    n_samples = int(duration * SAMPLE_RATE)
    return np.random.normal(0, 1, n_samples).astype(np.float32) * volume

# ------------------------------
# FX Processing Wrapper
# ------------------------------
fx_chain = FXChain(sample_rate=SAMPLE_RATE)

def process_effects(audio: np.ndarray,
                    reverb_amount=0.3,
                    delay_amount=0.3,
                    lowpass_cutoff=20000,
                    highpass_cutoff=20,
                    chorus_amount=0.0,
                    phaser_amount=0.0,
                    stereo_widen=0.0) -> np.ndarray:
    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=1)

    fx_chain.set_reverb(reverb_amount)
    fx_chain.set_delay(delay_amount)
    fx_chain.set_chorus(chorus_amount)
    fx_chain.set_phaser(phaser_amount)
    fx_chain.set_stereo_widen(stereo_widen)
    fx_chain.set_lowpass(lowpass_cutoff)
    fx_chain.set_highpass(highpass_cutoff)

    return fx_chain.apply(audio)
