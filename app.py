from scene_manager import SceneManager

class ProceduralMusicApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cinematic Procedural Ambient DAW")
        self.layout = QVBoxLayout()

        # Scene manager (auto evolution)
        self.scene_manager = SceneManager(SCALES, INSTRUMENTS, evolve=True)

        self.init_ui()
        self.setLayout(self.layout)

    def init_ui(self):
        # Tempo, scale, instrument UI
        self.tempo_slider = make_slider("Tempo (BPM)", 30, 200, 60, Qt.Orientation.Horizontal, self.layout)
        self.scale_combo = make_combo("Scale", list(SCALES.keys()), "minor", self.layout)
        self.inst_combo = make_combo("Instrument", INSTRUMENTS, "sine", self.layout)

        # Preset buttons
        self.layout.addWidget(QLabel("Presets"))
        btn_random = QPushButton("Random Preset")
        btn_random.clicked.connect(self.apply_random_preset)
        self.layout.addWidget(btn_random)

        btn_save = QPushButton("Save Preset")
        btn_save.clicked.connect(self.save_preset)
        self.layout.addWidget(btn_save)

        btn_load = QPushButton("Load Preset")
        btn_load.clicked.connect(self.load_preset)
        self.layout.addWidget(btn_load)

        # Scene evolution
        btn_next_scene = QPushButton("Next Scene")
        btn_next_scene.clicked.connect(self.apply_next_scene)
        self.layout.addWidget(btn_next_scene)

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

    def load_preset(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Preset", "", "JSON Files (*.json)")
        if fname:
            preset = load_preset(fname)
            self.load_preset_values(preset)

    def load_preset_values(self, values):
        """Update UI from preset dict."""
        if "tempo" in values: self.tempo_slider.setValue(values["tempo"])
        if "scale" in values: self.scale_combo.setCurrentText(values["scale"])
        if "instrument" in values: self.inst_combo.setCurrentText(values["instrument"])
        # (extend to effects etc.)

    def collect_values(self):
        """Grab current UI values into dict."""
        return {
            "tempo": self.tempo_slider.value(),
            "scale": self.scale_combo.currentText(),
            "instrument": self.inst_combo.currentText(),
            # (extend with effects etc.)
        }
