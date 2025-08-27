# audio_engine.py
import numpy as np
from audio_utils import process_effects, apply_pan
from procedural_generator import generate_procedural_chunk

class AudioEngine:
    def __init__(self, layer_lfos, ui_refs):
        """
        ui_refs = {
            "tempo": tempo_slider,
            "scale": scale_combo,
            "instrument": inst_combo,
            "arpeggio": arpeggio_checkbox,
            "reverb": reverb_slider,
            "delay": delay_slider,
            "chorus": chorus_slider,
            "phaser": phaser_slider,
            "stereo": stereo_slider,
            "lowpass": lowpass_slider,
            "highpass": highpass_slider,
            "evolving": evolving_checkbox,
            "lfo_tempo": lfo_tempo,
            "lfo_reverb": lfo_reverb,
            ...
        }
        """
        self.lfos = layer_lfos
        self.ui = ui_refs

    def generate_chunk(self, duration):
        tempo = self.ui["tempo"].value()
        if self.ui["evolving"].isChecked():
            tempo += self.ui["lfo_tempo"].step(duration)
        tempo = max(int(tempo), 20)

        layers = generate_procedural_chunk(
            duration,
            tempo,
            self.ui["scale"].currentText(),
            self.ui["instrument"].currentText(),
            use_arpeggio=self.ui["arpeggio"].isChecked(),
            return_layers=True
        )

        processed_layers = []
        for i, layer in enumerate(layers):
            lfo = self.lfos[i % len(self.lfos)]
            vol_mod = lfo["volume"].step(duration)
            pan_mod = lfo["pan"].step(duration)
            timbre_mod = lfo["timbre"].step(duration)

            mono = np.mean(layer, axis=1) * (1 + vol_mod)
            stereo = apply_pan(mono, pan_mod)

            if self.ui["instrument"].currentText() in ["fm_sine", "noise_pad"]:
                stereo *= (1 + 0.2 * timbre_mod)

            processed_layers.append(stereo)

        chunk = np.sum(processed_layers, axis=0)
        chunk = np.clip(chunk, -1, 1)

        # --- Global FX ---
        reverb = self.ui["reverb"].value()/100
        delay = self.ui["delay"].value()/100
        chorus = self.ui["chorus"].value()/100
        phaser = self.ui["phaser"].value()/100
        stereo_widen = self.ui["stereo"].value()/100

        if self.ui["evolving"].isChecked():
            reverb += self.ui["lfo_reverb"].step(duration)
            delay += self.ui["lfo_delay"].step(duration)
            chorus += self.ui["lfo_chorus"].step(duration)
            phaser += self.ui["lfo_phaser"].step(duration)
            stereo_widen += self.ui["lfo_stereo"].step(duration)

        return process_effects(
            chunk,
            reverb_amount=min(max(reverb, 0), 1),
            delay_amount=min(max(delay, 0), 1),
            lowpass_cutoff=self.ui["lowpass"].value(),
            highpass_cutoff=self.ui["highpass"].value(),
            chorus_amount=min(max(chorus, 0), 1),
            phaser_amount=min(max(phaser, 0), 1),
            stereo_widen=min(max(stereo_widen, 0), 1)
        )
