# app.py
import sys
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QLabel, QSpinBox, QDoubleSpinBox, QHBoxLayout, QFileDialog, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from scene_manager import SceneManager
from ui_builder import UIBuilder
from config import SCALES, INSTRUMENTS
from presets import save_preset, load_preset, random_preset
import logger


class ProceduralMusicApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cinematic Procedural Ambient DAW")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Scene manager (auto evolution)
        self.scene_manager = SceneManager(SCALES, INSTRUMENTS, evolve=True)

        # UI builder
        self.builder = UIBuilder(self.layout)

        self.init_ui()

    def init_ui(self):
        # ----- Section: Main Controls -----
        self.builder.add_title_label("Main Controls")
        self.tempo_slider = self.builder.add_slider("Tempo (BPM)", 30, 200, 60)
        self.scale_combo = self.builder.add_combo("Scale", list(SCALES.keys()), "minor")
        self.inst_combo = self.builder.add_combo("Instrument", INSTRUMENTS, "sine")

        self.builder.add_spacing(10)

        # ----- Section: Presets -----
        self.builder.add_title_label("Presets")
        btn_random = self.builder.add_button("Random Preset")
        btn_random.clicked.connect(self.apply_random_preset)
        btn_save = self.builder.add_button("Save Preset")
        btn_save.clicked.connect(self.save_preset)
        btn_load = self.builder.add_button("Load Preset")
        btn_load.clicked.connect(self.load_preset)

        self.builder.add_spacing(10)

        # ----- Section: Scene Evolution -----
        self.builder.add_title_label("Scene Evolution")
        btn_next_scene = self.builder.add_button("Next Scene")
        btn_next_scene.clicked.connect(self.apply_next_scene)

        self.builder.add_spacing(10)

        # ---------- Scene Preview ----------
        self.builder.add_title_label("Scene Preview")
        preview_box, preview_layout = self.builder.add_groupbox("Upcoming Scenes")
        nested = self.builder.nested_builder(preview_layout)

        # List to show next 5 scenes
        self.scene_list = QListWidget()
        nested.layout.addWidget(self.scene_list)

        # Controls for evolution parameters
        self.builder.add_title_label("Scene Evolution Settings")
        evolution_box, evolution_layout = self.builder.add_groupbox("Evolution Tweaks")
        evo_nested = self.builder.nested_builder(evolution_layout)

        # Example tweakable parameters
        self.evolution_speed = evo_nested.add_synced_slider_float(
            "Evolution Speed", 0.1, 5.0, 1.0, step=0.1
        )
        self.evolution_variation = evo_nested.add_synced_slider_float(
            "Variation Strength", 0.0, 1.0, 0.5, step=0.05
        )

        # Button to refresh preview manually
        btn_refresh_preview = evo_nested.add_button("Refresh Scene Preview")
        btn_refresh_preview.clicked.connect(self.refresh_scene_preview)

        # Automatically update preview when next scene is applied
        self.apply_next_scene()  # initial preview

    # -------------------- Preset Handling --------------------
    def apply_random_preset(self):
        preset = random_preset(SCALES, INSTRUMENTS)
        self.load_preset_values(preset)

    def apply_next_scene(self):
        scene = self.scene_manager.next_scene()
        self.load_preset_values(scene)

    def save_preset(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Preset", "", "JSON Files (*.json)")
        if fname:
            save_preset(fname, self.collect_values())
    
    def save_current_preset(self, preset_name: str):
        """
        Save the current preset with automatic versioning.
        """
        try:
            values = self.get_current_preset_values()  # dict of all preset params
            saved_name = save_preset_versioned(values, PRESET_FOLDER, preset_name, max_versions=5)
            info(f"Preset saved: {saved_name}")
        except Exception as e:
            error(f"Failed to save preset: {e}")

    def load_preset(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Preset", "", "JSON Files (*.json)")
        if fname:
            preset = load_preset(fname)
            self.load_preset_values(preset)

    # -------------------- Value Syncing --------------------
    def load_preset_values(self, values: dict):
        """Update UI from preset dictionary."""
        if "tempo" in values: self.tempo_slider.setValue(values["tempo"])
        if "scale" in values: self.scale_combo.setCurrentText(values["scale"])
        if "instrument" in values: self.inst_combo.setCurrentText(values["instrument"])

    def collect_values(self) -> dict:
        """Grab current UI values into dict."""
        return {
            "tempo": self.tempo_slider.value(),
            "scale": self.scale_combo.currentText(),
            "instrument": self.inst_combo.currentText(),
        }
    
    # -------------------- Scene Preview --------------------
    def refresh_scene_preview(self):
        """Update the list widget to show the next 5 upcoming scenes."""
        self.scene_list.clear()
        upcoming_scenes = self.scene_manager.peek_next_scenes(5)  # assuming this method exists
        for i, scene in enumerate(upcoming_scenes):
            item_text = f"Scene {i+1}: Tempo={scene.get('tempo', '')}, Scale={scene.get('scale', '')}, Instrument={scene.get('instrument', '')}"
            item = QListWidgetItem(item_text)
            self.scene_list.addItem(item)

    def apply_next_scene(self):
        scene = self.scene_manager.next_scene(
            speed=self.evolution_speed.spinbox.value(),
            variation=self.evolution_variation.spinbox.value()
        )
        self.load_preset_values(scene)
        self.refresh_scene_preview()
