# app.py
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QSlider, QSpinBox, QDoubleSpinBox, QPushButton, 
                             QComboBox, QCheckBox, QListWidget, QListWidgetItem, 
                             QGroupBox, QFrame, QFileDialog, QTabWidget, QStatusBar,
                             QSplitter, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor, QFont
from themes import DARK_THEME
from audio_engine import AudioEngine
from lfo import LFO, LayerLFO
from scene_manager import SceneManager
from presets import save_preset, load_preset, random_preset, list_presets
from recorder import Recorder
from logger import info, error, warn
import config

class ProceduralMusicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cinematic Procedural Ambient DAW")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.recorder = Recorder()
        self.scene_manager = SceneManager(config.SCALES, config.INSTRUMENTS, evolve=True)
        self.audio_engine = None
        self.is_playing = False
        self.current_preset = None
        
        # Setup UI
        self.setup_ui()
        self.apply_theme("dark")
        
        # Initialize audio after UI is set up
        self.init_audio_engine()
        
        # Setup timer for audio generation
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_audio_chunk)
        self.timer.start(100)  # Update every 100ms
        
        info("Application initialized")

    def setup_ui(self):
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Right panel for visualization and scene preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter)
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Setup tabs for different control sections
        self.setup_control_tabs(left_layout)
        self.setup_visualization(right_layout)
        
    def setup_control_tabs(self, layout):
        tabs = QTabWidget()
        
        # Main controls tab
        main_tab = QWidget()
        self.setup_main_controls(main_tab)
        tabs.addTab(main_tab, "Main")
        
        # Effects tab
        fx_tab = QWidget()
        self.setup_fx_controls(fx_tab)
        tabs.addTab(fx_tab, "Effects")
        
        # LFO tab
        lfo_tab = QWidget()
        self.setup_lfo_controls(lfo_tab)
        tabs.addTab(lfo_tab, "LFO")
        
        # Presets tab
        preset_tab = QWidget()
        self.setup_preset_controls(preset_tab)
        tabs.addTab(preset_tab, "Presets")
        
        layout.addWidget(tabs)
        
    def setup_main_controls(self, parent):
        layout = QVBoxLayout(parent)
        
        # Transport controls
        transport_group = QGroupBox("Transport")
        transport_layout = QVBoxLayout(transport_group)
        
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_playback)
        transport_layout.addWidget(self.play_button)
        
        self.record_button = QPushButton("Record")
        self.record_button.clicked.connect(self.toggle_recording)
        transport_layout.addWidget(self.record_button)
        
        layout.addWidget(transport_group)
        
        # Basic controls
        basic_group = QGroupBox("Basic Controls")
        basic_layout = QVBoxLayout(basic_group)
        
        # Tempo control
        tempo_layout = QHBoxLayout()
        tempo_layout.addWidget(QLabel("Tempo"))
        self.tempo_slider = QSlider(Qt.Orientation.Horizontal)
        self.tempo_slider.setRange(30, 200)
        self.tempo_slider.setValue(60)
        self.tempo_slider.valueChanged.connect(self.update_tempo)
        tempo_layout.addWidget(self.tempo_slider)
        self.tempo_label = QLabel("60")
        tempo_layout.addWidget(self.tempo_label)
        basic_layout.addLayout(tempo_layout)
        
        # Scale selection
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale"))
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(config.SCALES.keys())
        self.scale_combo.currentTextChanged.connect(self.update_scale)
        scale_layout.addWidget(self.scale_combo)
        basic_layout.addLayout(scale_layout)
        
        # Instrument selection
        instrument_layout = QHBoxLayout()
        instrument_layout.addWidget(QLabel("Instrument"))
        self.instrument_combo = QComboBox()
        self.instrument_combo.addItems(config.INSTRUMENTS)
        self.instrument_combo.currentTextChanged.connect(self.update_instrument)
        instrument_layout.addWidget(self.instrument_combo)
        basic_layout.addLayout(instrument_layout)
        
        # Arpeggio toggle
        self.arpeggio_check = QCheckBox("Use Arpeggio")
        self.arpeggio_check.stateChanged.connect(self.update_arpeggio)
        basic_layout.addWidget(self.arpeggio_check)
        
        # Evolving toggle
        self.evolving_check = QCheckBox("Evolving")
        self.evolving_check.stateChanged.connect(self.update_evolving)
        basic_layout.addWidget(self.evolving_check)
        
        layout.addWidget(basic_group)
        
    def setup_fx_controls(self, parent):
        layout = QVBoxLayout(parent)
        
        # Reverb control
        reverb_layout = QHBoxLayout()
        reverb_layout.addWidget(QLabel("Reverb"))
        self.reverb_slider = QSlider(Qt.Orientation.Horizontal)
        self.reverb_slider.setRange(0, 100)
        self.reverb_slider.setValue(30)
        reverb_layout.addWidget(self.reverb_slider)
        layout.addLayout(reverb_layout)
        
        # Delay control
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Delay"))
        self.delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.delay_slider.setRange(0, 100)
        self.delay_slider.setValue(30)
        delay_layout.addWidget(self.delay_slider)
        layout.addLayout(delay_layout)
        
        # Chorus control
        chorus_layout = QHBoxLayout()
        chorus_layout.addWidget(QLabel("Chorus"))
        self.chorus_slider = QSlider(Qt.Orientation.Horizontal)
        self.chorus_slider.setRange(0, 100)
        self.chorus_slider.setValue(0)
        chorus_layout.addWidget(self.chorus_slider)
        layout.addLayout(chorus_layout)
        
        # Phaser control
        phaser_layout = QHBoxLayout()
        phaser_layout.addWidget(QLabel("Phaser"))
        self.phaser_slider = QSlider(Qt.Orientation.Horizontal)
        self.phaser_slider.setRange(0, 100)
        self.phaser_slider.setValue(0)
        phaser_layout.addWidget(self.phaser_slider)
        layout.addLayout(phaser_layout)
        
        # Stereo control
        stereo_layout = QHBoxLayout()
        stereo_layout.addWidget(QLabel("Stereo Width"))
        self.stereo_slider = QSlider(Qt.Orientation.Horizontal)
        self.stereo_slider.setRange(0, 100)
        self.stereo_slider.setValue(0)
        stereo_layout.addWidget(self.stereo_slider)
        layout.addLayout(stereo_layout)
        
        # Filter controls
        filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout(filter_group)
        
        lowpass_layout = QHBoxLayout()
        lowpass_layout.addWidget(QLabel("Lowpass"))
        self.lowpass_slider = QSlider(Qt.Orientation.Horizontal)
        self.lowpass_slider.setRange(20, 20000)
        self.lowpass_slider.setValue(20000)
        lowpass_layout.addWidget(self.lowpass_slider)
        filter_layout.addLayout(lowpass_layout)
        
        highpass_layout = QHBoxLayout()
        highpass_layout.addWidget(QLabel("Highpass"))
        self.highpass_slider = QSlider(Qt.Orientation.Horizontal)
        self.highpass_slider.setRange(20, 20000)
        self.highpass_slider.setValue(20)
        highpass_layout.addWidget(self.highpass_slider)
        filter_layout.addLayout(highpass_layout)
        
        layout.addWidget(filter_group)
        
    def setup_lfo_controls(self, parent):
        layout = QVBoxLayout(parent)
        
        # Global LFO controls
        global_group = QGroupBox("Global LFO")
        global_layout = QVBoxLayout(global_group)
        
        # Add LFO controls for various parameters
        lfo_params = ["Tempo", "Reverb", "Delay", "Chorus", "Phaser", "Stereo"]
        self.lfo_controls = {}
        
        for param in lfo_params:
            param_layout = QHBoxLayout()
            param_layout.addWidget(QLabel(f"{param} LFO Rate"))
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 1000)
            slider.setValue(50)
            param_layout.addWidget(slider)
            
            self.lfo_controls[f"lfo_{param.lower()}"] = slider
            global_layout.addLayout(param_layout)
        
        layout.addWidget(global_group)
        
        # Layer LFO controls
        layer_group = QGroupBox("Layer LFO")
        layer_layout = QVBoxLayout(layer_group)
        
        for i in range(4):
            layer_frame = QGroupBox(f"Layer {i+1}")
            layer_frame_layout = QVBoxLayout(layer_frame)
            
            for param in ["Volume", "Pan", "Timbre"]:
                param_layout = QHBoxLayout()
                param_layout.addWidget(QLabel(param))
                
                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setRange(0, 1000)
                slider.setValue(100 if param == "Volume" else 500)
                param_layout.addWidget(slider)
                
                self.lfo_controls[f"layer_{i}_{param.lower()}"] = slider
                layer_frame_layout.addLayout(param_layout)
            
            layer_layout.addWidget(layer_frame)
        
        layout.addWidget(layer_group)
        
    def setup_preset_controls(self, parent):
        layout = QVBoxLayout(parent)
        
        # Preset list
        preset_list_group = QGroupBox("Presets")
        preset_list_layout = QVBoxLayout(preset_list_group)
        
        self.preset_list = QListWidget()
        self.refresh_preset_list()
        preset_list_layout.addWidget(self.preset_list)
        
        # Preset buttons
        preset_buttons_layout = QHBoxLayout()
        
        self.load_preset_button = QPushButton("Load")
        self.load_preset_button.clicked.connect(self.load_selected_preset)
        preset_buttons_layout.addWidget(self.load_preset_button)
        
        self.save_preset_button = QPushButton("Save")
        self.save_preset_button.clicked.connect(self.save_preset)
        preset_buttons_layout.addWidget(self.save_preset_button)
        
        self.delete_preset_button = QPushButton("Delete")
        self.delete_preset_button.clicked.connect(self.delete_preset)
        preset_buttons_layout.addWidget(self.delete_preset_button)
        
        preset_list_layout.addLayout(preset_buttons_layout)
        layout.addWidget(preset_list_group)
        
        # Randomize button
        self.randomize_button = QPushButton("Randomize")
        self.randomize_button.clicked.connect(self.randomize_preset)
        layout.addWidget(self.randomize_button)
        
        # Scene evolution controls
        scene_group = QGroupBox("Scene Evolution")
        scene_layout = QVBoxLayout(scene_group)
        
        self.next_scene_button = QPushButton("Next Scene")
        self.next_scene_button.clicked.connect(self.next_scene)
        scene_layout.addWidget(self.next_scene_button)
        
        self.scene_preview = QListWidget()
        scene_layout.addWidget(self.scene_preview)
        
        layout.addWidget(scene_group)
        
    def setup_visualization(self, layout):
        # Audio visualization placeholder
        viz_group = QGroupBox("Audio Visualization")
        viz_layout = QVBoxLayout(viz_group)
        
        self.viz_label = QLabel("Audio visualization will appear here")
        self.viz_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viz_label.setMinimumHeight(200)
        viz_layout.addWidget(self.viz_label)
        
        # Level meters
        meters_layout = QHBoxLayout()
        
        self.left_meter = QProgressBar()
        self.left_meter.setOrientation(Qt.Orientation.Vertical)
        self.left_meter.setRange(0, 100)
        meters_layout.addWidget(self.left_meter)
        
        self.right_meter = QProgressBar()
        self.right_meter.setOrientation(Qt.Orientation.Vertical)
        self.right_meter.setRange(0, 100)
        meters_layout.addWidget(self.right_meter)
        
        viz_layout.addLayout(meters_layout)
        layout.addWidget(viz_group)
        
        # Scene preview
        scene_preview_group = QGroupBox("Scene Timeline")
        scene_preview_layout = QVBoxLayout(scene_preview_group)
        
        self.timeline = QListWidget()
        scene_preview_layout.addWidget(self.timeline)
        
        layout.addWidget(scene_preview_group)
        
    def apply_theme(self, theme_name):
        """Apply a theme to the application"""
        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet("")  # Default theme
            
    def init_audio_engine(self):
        """Initialize the audio engine with current UI values"""
        try:
            # Create LFOs from UI controls
            layer_lfos = []
            for i in range(4):
                volume_lfo = LFO(
                    rate=self.lfo_controls[f"layer_{i}_volume"].value() / 100000,
                    amplitude=0.3
                )
                pan_lfo = LFO(
                    rate=self.lfo_controls[f"layer_{i}_pan"].value() / 100000,
                    amplitude=0.5
                )
                timbre_lfo = LFO(
                    rate=self.lfo_controls[f"layer_{i}_timbre"].value() / 100000,
                    amplitude=0.5
                )
                layer_lfos.append({
                    "volume": volume_lfo,
                    "pan": pan_lfo,
                    "timbre": timbre_lfo
                })
            
            # Create global LFOs
            global_lfos = {}
            for param in ["tempo", "reverb", "delay", "chorus", "phaser", "stereo"]:
                global_lfos[f"lfo_{param}"] = LFO(
                    rate=self.lfo_controls[f"lfo_{param}"].value() / 100000,
                    amplitude=0.5
                )
            
            # UI references for audio engine
            ui_refs = {
                "tempo": self.tempo_slider,
                "scale": self.scale_combo,
                "instrument": self.instrument_combo,
                "arpeggio": self.arpeggio_check,
                "reverb": self.reverb_slider,
                "delay": self.delay_slider,
                "chorus": self.chorus_slider,
                "phaser": self.phaser_slider,
                "stereo": self.stereo_slider,
                "lowpass": self.lowpass_slider,
                "highpass": self.highpass_slider,
                "evolving": self.evolving_check,
                **global_lfos
            }
            
            self.audio_engine = AudioEngine(layer_lfos, ui_refs)
            info("Audio engine initialized")
            
        except Exception as e:
            error(f"Failed to initialize audio engine: {e}")
            
    def generate_audio_chunk(self):
        """Generate a chunk of audio data"""
        if self.is_playing and self.audio_engine:
            try:
                # Generate 100ms of audio
                chunk = self.audio_engine.generate_chunk(0.1)
                
                # Update level meters
                if chunk.size > 0:
                    left_level = np.abs(chunk[:, 0]).mean() * 100
                    right_level = np.abs(chunk[:, 1]).mean() * 100
                    self.left_meter.setValue(int(left_level))
                    self.right_meter.setValue(int(right_level))
                
                # Record if recording is enabled
                if self.recorder.recording:
                    self.recorder.add_frame(chunk.tobytes())
                    
            except Exception as e:
                error(f"Error generating audio chunk: {e}")
                
    def toggle_playback(self):
        """Toggle playback state"""
        self.is_playing = not self.is_playing
        self.play_button.setText("Pause" if self.is_playing else "Play")
        self.status_bar.showMessage("Playing" if self.is_playing else "Paused")
        
    def toggle_recording(self):
        """Toggle recording state"""
        if self.recorder.recording:
            filename = self.recorder.stop()
            self.record_button.setText("Record")
            self.status_bar.showMessage(f"Recording saved to {filename}")
        else:
            self.recorder.start()
            self.record_button.setText("Stop Recording")
            self.status_bar.showMessage("Recording...")
            
    def update_tempo(self, value):
        """Update tempo value"""
        self.tempo_label.setText(str(value))
        
    def update_scale(self, scale):
        """Update scale selection"""
        pass  # Handled by audio engine
        
    def update_instrument(self, instrument):
        """Update instrument selection"""
        pass  # Handled by audio engine
        
    def update_arpeggio(self, state):
        """Update arpeggio setting"""
        pass  # Handled by audio engine
        
    def update_evolving(self, state):
        """Update evolving setting"""
        pass  # Handled by audio engine
        
    def refresh_preset_list(self):
        """Refresh the list of available presets"""
        self.preset_list.clear()
        presets = list_presets(config.PRESET_FOLDER)
        self.preset_list.addItems(presets)
        
    def load_selected_preset(self):
        """Load the selected preset"""
        selected = self.preset_list.currentItem()
        if selected:
            preset_name = selected.text()
            self.load_preset(preset_name)
            
    def load_preset(self, preset_name):
        """Load a preset by name"""
        try:
            preset_path = os.path.join(config.PRESET_FOLDER, preset_name)
            preset = load_preset(preset_path)
            self.apply_preset(preset)
            self.current_preset = preset_name
            self.status_bar.showMessage(f"Loaded preset: {preset_name}")
        except Exception as e:
            error(f"Failed to load preset: {e}")
            
    def save_preset(self):
        """Save current settings as a preset"""
        try:
            preset_name, ok = QFileDialog.getSaveFileName(
                self, "Save Preset", config.PRESET_FOLDER, "JSON Files (*.json)"
            )
            if ok and preset_name:
                if not preset_name.endswith(".json"):
                    preset_name += ".json"
                    
                preset = self.collect_preset_data()
                save_preset(preset_name, preset)
                self.refresh_preset_list()
                self.status_bar.showMessage(f"Preset saved: {preset_name}")
        except Exception as e:
            error(f"Failed to save preset: {e}")
            
    def delete_preset(self):
        """Delete the selected preset"""
        selected = self.preset_list.currentItem()
        if selected:
            preset_name = selected.text()
            try:
                preset_path = os.path.join(config.PRESET_FOLDER, preset_name)
                os.remove(preset_path)
                self.refresh_preset_list()
                self.status_bar.showMessage(f"Deleted preset: {preset_name}")
            except Exception as e:
                error(f"Failed to delete preset: {e}")
                
    def randomize_preset(self):
        """Apply a random preset"""
        try:
            preset = random_preset(config.SCALES, config.INSTRUMENTS)
            self.apply_preset(preset)
            self.status_bar.showMessage("Applied random preset")
        except Exception as e:
            error(f"Failed to apply random preset: {e}")
            
    def next_scene(self):
        """Move to the next scene"""
        try:
            scene = self.scene_manager.next_scene()
            self.apply_preset(scene)
            self.update_scene_preview()
            self.status_bar.showMessage("Applied next scene")
        except Exception as e:
            error(f"Failed to apply next scene: {e}")
            
    def collect_preset_data(self):
        """Collect current settings into a preset dictionary"""
        return {
            "tempo": self.tempo_slider.value(),
            "scale": self.scale_combo.currentText(),
            "instrument": self.instrument_combo.currentText(),
            "use_arpeggio": self.arpeggio_check.isChecked(),
            "reverb": self.reverb_slider.value(),
            "delay": self.delay_slider.value(),
            "chorus": self.chorus_slider.value(),
            "phaser": self.phaser_slider.value(),
            "stereo_widen": self.stereo_slider.value(),
            "lowpass": self.lowpass_slider.value(),
            "highpass": self.highpass_slider.value(),
            "evolving": self.evolving_check.isChecked()
        }
        
    def apply_preset(self, preset):
        """Apply a preset dictionary to the UI"""
        try:
            if "tempo" in preset:
                self.tempo_slider.setValue(preset["tempo"])
            if "scale" in preset:
                self.scale_combo.setCurrentText(preset["scale"])
            if "instrument" in preset:
                self.instrument_combo.setCurrentText(preset["instrument"])
            if "use_arpeggio" in preset:
                self.arpeggio_check.setChecked(preset["use_arpeggio"])
            if "reverb" in preset:
                self.reverb_slider.setValue(preset["reverb"])
            if "delay" in preset:
                self.delay_slider.setValue(preset["delay"])
            if "chorus" in preset:
                self.chorus_slider.setValue(preset["chorus"])
            if "phaser" in preset:
                self.phaser_slider.setValue(preset["phaser"])
            if "stereo_widen" in preset:
                self.stereo_slider.setValue(preset["stereo_widen"])
            if "lowpass" in preset:
                self.lowpass_slider.setValue(preset["lowpass"])
            if "highpass" in preset:
                self.highpass_slider.setValue(preset["highpass"])
            if "evolving" in preset:
                self.evolving_check.setChecked(preset["evolving"])
                
        except Exception as e:
            error(f"Failed to apply preset: {e}")
            
    def update_scene_preview(self):
        """Update the scene preview list"""
        self.scene_preview.clear()
        # Add logic to preview upcoming scenes
        
    def closeEvent(self, event):
        """Handle application close"""
        if self.recorder.recording:
            self.recorder.stop()
        self.timer.stop()
        event.accept()