# recorder.py
import os
import wave
from datetime import datetime
import numpy as np

class Recorder:
    def __init__(self, sample_rate=44100, channels=2, bit_depth=16, export_dir="exports"):
        self.sample_rate = sample_rate
        self.channels = channels
        self.bit_depth = bit_depth
        self.export_dir = export_dir
        self.recording = False
        self.frames = []

        os.makedirs(export_dir, exist_ok=True)

    def start(self):
        """Begin recording audio frames."""
        self.frames = []
        self.recording = True
        print("[Recorder] Started recording.")

    def stop(self):
        """Stop recording and save to WAV."""
        self.recording = False
        print("[Recorder] Stopped recording.")
        return self.save_wav()

    def add_frame(self, frame_bytes):
        """Append a raw PCM frame (bytes) to recording buffer."""
        if self.recording:
            self.frames.append(frame_bytes)

    def add_audio_data(self, audio_data: np.ndarray):
        """Add numpy array audio data to recording."""
        if self.recording:
            # Convert to 16-bit PCM
            audio_int16 = (audio_data * 32767).astype(np.int16)
            self.frames.append(audio_int16.tobytes())

    def save_wav(self):
        """Save collected frames to a timestamped WAV file."""
        if not self.frames:
            print("[Recorder] No audio recorded.")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.export_dir}/recording_{timestamp}.wav"

        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.bit_depth // 8)
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        print(f"[Recorder] Saved: {filename}")
        return filename