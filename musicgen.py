# main.py (Fixed chord progression selection)
import mido
import numpy as np
import pyaudio
import threading
import time
import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty

# Set window size
Window.size = (1000, 750)

class AdvancedVisualizer(BoxLayout):
    def __init__(self, **kwargs):
        super(AdvancedVisualizer, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.notes_history = []
        self.active_notes = []
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        
    def update_graphics(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Background
            Color(0.05, 0.05, 0.1, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Draw frequency spectrum visualization
            if self.notes_history:
                bar_width = self.width / max(1, len(self.notes_history))
                max_height = self.height * 0.7
                
                for i, note in enumerate(self.notes_history[-50:]):  # Show last 50 notes
                    intensity = max(0.1, (note - 40) / 60)  # Normalize note (40-100) to 0-1
                    bar_height = max_height * intensity
                    
                    # Color based on note position
                    hue = (note - 40) / 60
                    Color(hue, 0.7, 1 - hue, 0.8)
                    
                    Rectangle(
                        pos=(self.x + i * bar_width, self.y + self.height * 0.15),
                        size=(bar_width * 0.8, bar_height)
                    )
            
            # Draw active notes
            if self.active_notes:
                note_radius = min(self.width, self.height) * 0.05
                for i, note in enumerate(self.active_notes[-10:]):  # Show last 10 active notes
                    x_pos = self.x + self.width * 0.5 + (i - 5) * note_radius * 3
                    y_pos = self.y + self.height * 0.8
                    
                    # Animated circle
                    Color(0.2, 0.8, 1, 0.7)
                    Ellipse(
                        pos=(x_pos - note_radius/2, y_pos - note_radius/2),
                        size=(note_radius, note_radius)
                    )
    
    def add_note(self, note):
        # Schedule UI update on main thread
        Clock.schedule_once(lambda dt: self._add_note_ui(note), 0)
    
    def _add_note_ui(self, note):
        self.notes_history.append(note)
        self.active_notes.append(note)
        self.update_graphics()
        # Remove note after animation
        Clock.schedule_once(lambda dt: self._remove_note_ui(note), 0.3)
    
    def _remove_note_ui(self, note):
        if note in self.active_notes:
            self.active_notes.remove(note)
            self.update_graphics()

class PresetManager:
    def __init__(self):
        self.presets_file = 'music_presets.json'
        self.presets = self.load_presets()
    
    def load_presets(self):
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, 'r') as f:
                    return json.load(f)
            except:
                return self.get_default_presets()
        return self.get_default_presets()
    
    def get_default_presets(self):
        return {
            "Epic Adventure": {"tempo": 140, "key": "D", "scale": "major", "sections": 3},
            "Jazz Lounge": {"tempo": 90, "key": "Bb", "scale": "minor", "sections": 2},
            "Classical": {"tempo": 100, "key": "C", "scale": "major", "sections": 4},
            "Ambient": {"tempo": 70, "key": "E", "scale": "pentatonic", "sections": 2},
            "Rock Anthem": {"tempo": 160, "key": "A", "scale": "major", "sections": 3},
            "Blues Progression": {"tempo": 120, "key": "A", "scale": "minor", "sections": 3},
            "Pop Hit": {"tempo": 125, "key": "F", "scale": "major", "sections": 2}
        }
    
    def save_presets(self):
        with open(self.presets_file, 'w') as f:
            json.dump(self.presets, f, indent=2)
    
    def add_preset(self, name, params):
        self.presets[name] = params
        self.save_presets()
    
    def delete_preset(self, name):
        if name in self.presets:
            del self.presets[name]
            self.save_presets()

class MusicGenerator:
    def __init__(self, tempo=120, key='C', scale='major'):
        self.tempo = tempo
        self.key = key
        self.scale = scale
        self.scale_notes = self._generate_scale(key, scale)
        self.composition = []
        self.sample_rate = 44100
        self.pyaudio_instance = pyaudio.PyAudio()
        self.is_playing = False
        self.play_thread = None
        self.current_note_callback = None
        self.playback_finished_callback = None
        # Extended chord progressions library
        self.chord_progressions = {
            'pop': [
                [1, 5, 6, 4],      # I-V-vi-IV (most popular)
                [1, 6, 4, 5],      # I-vi-IV-V
                [1, 4, 6, 5],      # I-IV-vi-V
                [6, 4, 1, 5],      # vi-IV-I-V
                [4, 1, 5, 6]       # IV-I-V-vi
            ],
            'jazz': [
                [2, 5, 1, 6],      # ii-V-I-vi
                [1, 6, 2, 5],      # I-vi-ii-V
                [3, 6, 2, 5],      # iii-vi-ii-V
                [1, 4, 2, 5]       # I-IV-ii-V
            ],
            'blues': [
                [1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 1],  # 12-bar blues
                [1, 4, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5]   # Blues variation
            ],
            'classical': [
                [1, 4, 6, 5, 1],   # Classical progression
                [1, 5, 6, 3, 4, 1, 4, 5],  # Pachelbel's Canon
                [6, 3, 4, 1, 6, 3, 4, 1]   # Andalusian cadence
            ],
            'rock': [
                [1, 5, 6, 4, 1, 5, 1, 5],  # Rock progression
                [1, 4, 1, 5, 1, 4, 1, 5],  # Classic rock
                [1, 5, 4, 6, 1, 5, 4, 6]   # Rock variation
            ],
            'ambient': [
                [1, 5, 6, 3],      # Ambient progression
                [6, 4, 1, 5],      # vi-IV-I-V
                [1, 6, 4, 5, 1]    # Extended ambient
            ]
        }
        
    def _generate_scale(self, key, scale_type):
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key_index = notes.index(key)
        
        scales = {
            'major': [0, 2, 4, 5, 7, 9, 11],
            'minor': [0, 2, 3, 5, 7, 8, 10],
            'pentatonic': [0, 2, 4, 7, 9]
        }
        
        scale_pattern = scales.get(scale_type, scales['major'])
        return [(key_index + interval) % 12 for interval in scale_pattern] * 2
    
    def generate_melody(self, length=16, note_range=(60, 84)):
        melody = []
        for _ in range(length):
            note_offset = np.random.choice(self.scale_notes)
            octave = np.random.choice([4, 5])
            note = 12 * octave + note_offset
            note = max(note_range[0], min(note_range[1], note))
            duration = np.random.choice([240, 480, 960], p=[0.5, 0.4, 0.1])
            melody.append((note, duration))
        return melody
    
    def create_chord_progression(self, progression_style='pop', length=4):
        # Select progression based on style
        if progression_style in self.chord_progressions:
            progressions = self.chord_progressions[progression_style]
            # Randomly select one progression from the list
            progression = progressions[np.random.randint(0, len(progressions))]
        else:
            # Default to pop if style not found
            progression = [1, 5, 6, 4]
        
        # Chord types for major scale degrees
        chord_types = {
            1: '', 2: 'm', 3: 'm', 4: '', 5: '', 6: 'm', 7: 'dim'
        }
        
        chords = []
        for degree in progression:
            # Get root note (degree - 1 because of 0-indexing)
            root_index = (degree - 1) % len(self.scale_notes)
            root_note = self.scale_notes[root_index] + 60  # Start at C4
            
            # Determine chord type
            chord_type = chord_types.get(degree, '')
            
            # Build triad
            if chord_type == 'm':  # Minor
                chord = [root_note, root_note + 3, root_note + 7]
            elif chord_type == 'dim':  # Diminished
                chord = [root_note, root_note + 3, root_note + 6]
            else:  # Major
                chord = [root_note, root_note + 4, root_note + 7]
            
            chords.append(chord)
        
        # Repeat to desired length
        return (chords * ((length * 4) // len(chords) + 1))[:length * 4]
    
    def compose_song(self, sections=2, style='pop'):
        self.composition = []
        for section in range(sections):
            chords = self.create_chord_progression(progression_style=style)
            melody = self.generate_melody(length=len(chords))
            self.composition.append({
                'chords': chords,
                'melody': melody
            })
    
    def save_midi(self, filename='composition.mid'):
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        tempo = mido.bpm2tempo(self.tempo)
        track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        
        for section in self.composition:
            for chord in section['chords']:
                for note in chord:
                    track.append(mido.Message('note_on', channel=0, note=note, velocity=64, time=0))
                track.append(mido.Message('note_off', channel=0, note=chord[0], velocity=64, time=480))
                for note in chord[1:]:
                    track.append(mido.Message('note_off', channel=0, note=note, velocity=64, time=0))
            
            melody_track = mido.MidiTrack()
            mid.tracks.append(melody_track)
            
            for note, duration in section['melody']:
                melody_track.append(mido.Message('note_on', channel=1, note=note, velocity=80, time=0))
                melody_track.append(mido.Message('note_off', channel=1, note=note, velocity=80, time=duration))
        
        mid.save(filename)
        return filename
    
    def _note_to_frequency(self, note):
        return 440 * (2 ** ((note - 69) / 12))
    
    def _generate_sine_wave(self, frequency, duration, volume=0.3):
        frames = int(self.sample_rate * duration)
        arr = np.zeros(frames)
        
        for i in range(frames):
            arr[i] = volume * np.sin(2 * np.pi * frequency * i / self.sample_rate)
        
        return arr.astype(np.float32)
    
    def _play_notes(self, notes, duration):
        if not notes or not self.is_playing:
            time.sleep(duration)
            return
            
        # Notify visualizer (scheduled on main thread)
        if self.current_note_callback and notes:
            self.current_note_callback(notes[0])
            
        waves = []
        for note in notes:
            freq = self._note_to_frequency(note)
            wave = self._generate_sine_wave(freq, duration, volume=0.2)
            waves.append(wave)
        
        if waves:
            mixed = np.sum(waves, axis=0) / len(waves)
            mixed = np.clip(mixed, -1.0, 1.0)
            
            try:
                stream = self.pyaudio_instance.open(
                    format=pyaudio.paFloat32,
                    channels=1,
                    rate=self.sample_rate,
                    output=True
                )
                stream.write(mixed.tobytes())
                stream.stop_stream()
                stream.close()
            except Exception as e:
                print(f"Audio error: {e}")
    
    def play_composition(self, note_callback=None, finished_callback=None):
        self.current_note_callback = note_callback
        self.playback_finished_callback = finished_callback
        
        def play_thread():
            self.is_playing = True
            beat_duration = 60 / self.tempo
            
            try:
                for section in self.composition:
                    if not self.is_playing:
                        break
                        
                    chords = section['chords']
                    melody = section['melody']
                    
                    chord_index = 0
                    melody_index = 0
                    melody_time_played = 0
                    
                    while melody_index < len(melody) and self.is_playing:
                        current_chord = chords[chord_index % len(chords)]
                        melody_note, melody_duration = melody[melody_index]
                        melody_duration_sec = (melody_duration / 480) * beat_duration
                        
                        self._play_notes(current_chord + [melody_note], melody_duration_sec)
                        
                        melody_time_played += melody_duration
                        if melody_time_played >= 480:
                            chord_index += 1
                            melody_time_played = 0
                        
                        melody_index += 1
            except Exception as e:
                print(f"Playback error: {e}")
            finally:
                self.is_playing = False
                # Schedule finished callback on main thread
                if self.playback_finished_callback:
                    Clock.schedule_once(lambda dt: self.playback_finished_callback(), 0)
        
        if not self.is_playing:
            self.play_thread = threading.Thread(target=play_thread)
            self.play_thread.daemon = True
            self.play_thread.start()
    
    def stop_playback(self):
        self.is_playing = False
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)  # Wait up to 1 second
    
    def close(self):
        self.stop_playback()
        try:
            self.pyaudio_instance.terminate()
        except:
            pass

class MusicGeneratorApp(App):
    def build(self):
        self.title = "Professional Music Generator Studio"
        self.generator = MusicGenerator()
        self.preset_manager = PresetManager()
        
        # Main layout with tabs
        self.main_layout = TabbedPanel(do_default_tab=False)
        
        # Create tabs
        self.create_composer_tab()
        self.create_presets_tab()
        self.create_about_tab()
        
        return self.main_layout
    
    def create_composer_tab(self):
        composer_tab = TabbedPanelItem(text='Composer')
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        header = Label(
            text="AI Music Composer Studio",
            font_size=28,
            bold=True,
            color=(0.2, 0.8, 1, 1)
        )
        header_layout.add_widget(header)
        
        # Info panel
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.3)
        self.tempo_display = Label(text="Tempo: 120 BPM", font_size=14)
        self.key_display = Label(text="Key: C Major", font_size=14)
        info_layout.add_widget(self.tempo_display)
        info_layout.add_widget(self.key_display)
        header_layout.add_widget(info_layout)
        
        main_layout.add_widget(header_layout)
        
        # Main content area
        content_layout = BoxLayout(orientation='horizontal', spacing=15)
        
        # Controls panel
        controls_panel = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=10)
        
        # Parameters section
        params_box = BoxLayout(orientation='vertical', spacing=10)
        params_header = Label(text="COMPOSITION PARAMETERS", size_hint_y=None, height=30, 
                             bold=True, color=(0.7, 0.7, 1, 1))
        params_box.add_widget(params_header)
        
        # Tempo control
        tempo_layout = BoxLayout(orientation='horizontal')
        tempo_layout.add_widget(Label(text="Tempo:", size_hint_x=0.3))
        self.tempo_slider = Slider(min=60, max=200, value=120)
        self.tempo_value = Label(text="120 BPM", size_hint_x=0.3)
        self.tempo_slider.bind(value=self.on_tempo_change)
        tempo_layout.add_widget(self.tempo_slider)
        tempo_layout.add_widget(self.tempo_value)
        params_box.add_widget(tempo_layout)
        
        # Key selection
        key_layout = BoxLayout(orientation='horizontal')
        key_layout.add_widget(Label(text="Key:", size_hint_x=0.3))
        self.key_spinner = Spinner(
            text='C',
            values=('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
        )
        key_layout.add_widget(self.key_spinner)
        params_box.add_widget(key_layout)
        
        # Scale selection
        scale_layout = BoxLayout(orientation='horizontal')
        scale_layout.add_widget(Label(text="Scale:", size_hint_x=0.3))
        self.scale_spinner = Spinner(
            text='major',
            values=('major', 'minor', 'pentatonic')
        )
        scale_layout.add_widget(self.scale_spinner)
        params_box.add_widget(scale_layout)
        
        # Style selection
        style_layout = BoxLayout(orientation='horizontal')
        style_layout.add_widget(Label(text="Style:", size_hint_x=0.3))
        self.style_spinner = Spinner(
            text='pop',
            values=('pop', 'jazz', 'blues', 'classical', 'rock', 'ambient')
        )
        style_layout.add_widget(self.style_spinner)
        params_box.add_widget(style_layout)
        
        # Sections
        sections_layout = BoxLayout(orientation='horizontal')
        sections_layout.add_widget(Label(text="Sections:", size_hint_x=0.3))
        self.sections_slider = Slider(min=1, max=5, value=2, step=1)
        self.sections_value = Label(text="2", size_hint_x=0.3)
        self.sections_slider.bind(value=self.on_sections_change)
        sections_layout.add_widget(self.sections_slider)
        sections_layout.add_widget(self.sections_value)
        params_box.add_widget(sections_layout)
        
        controls_panel.add_widget(params_box)
        
        # Action buttons
        buttons_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.4)
        buttons_header = Label(text="ACTIONS", size_hint_y=None, height=30, 
                              bold=True, color=(0.7, 0.7, 1, 1))
        buttons_box.add_widget(buttons_header)
        
        self.generate_btn = Button(
            text="Generate Composition",
            background_color=(0.2, 0.6, 1, 1),
            font_size=16,
            size_hint_y=0.25
        )
        self.generate_btn.bind(on_press=self.generate_composition)
        buttons_box.add_widget(self.generate_btn)
        
        self.play_btn = Button(
            text="▶ Play Composition",
            background_color=(0.2, 0.8, 0.2, 1),
            font_size=16,
            size_hint_y=0.25
        )
        self.play_btn.bind(on_press=self.toggle_playback)
        buttons_box.add_widget(self.play_btn)
        
        self.save_btn = Button(
            text="💾 Export MIDI File",
            background_color=(0.8, 0.6, 0.2, 1),
            font_size=16,
            size_hint_y=0.25
        )
        self.save_btn.bind(on_press=self.save_midi)
        buttons_box.add_widget(self.save_btn)
        
        self.stop_btn = Button(
            text="⏹ Stop Playback",
            background_color=(0.8, 0.2, 0.2, 1),
            font_size=16,
            size_hint_y=0.25
        )
        self.stop_btn.bind(on_press=self.stop_playback)
        buttons_box.add_widget(self.stop_btn)
        
        controls_panel.add_widget(buttons_box)
        content_layout.add_widget(controls_panel)
        
        # Visualization area
        visual_box = BoxLayout(orientation='vertical', spacing=10)
        visual_header = Label(text="MUSIC VISUALIZATION", size_hint_y=None, height=30, 
                             bold=True, color=(0.7, 0.7, 1, 1))
        visual_box.add_widget(visual_header)
        
        self.visualizer = AdvancedVisualizer()
        visual_box.add_widget(self.visualizer)
        
        # Progress bar
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=20)
        visual_box.add_widget(self.progress_bar)
        
        content_layout.add_widget(visual_box)
        main_layout.add_widget(content_layout)
        
        # Status bar
        self.status_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.status_label = Label(
            text="Ready to create music • Adjust parameters and click Generate",
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        self.status_bar.add_widget(self.status_label)
        main_layout.add_widget(self.status_bar)
        
        composer_tab.add_widget(main_layout)
        self.main_layout.add_widget(composer_tab)
    
    def create_presets_tab(self):
        presets_tab = TabbedPanelItem(text='Presets')
        
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Header
        header = Label(
            text="Composition Presets",
            font_size=24,
            bold=True,
            size_hint_y=None,
            height=50
        )
        main_layout.add_widget(header)
        
        # Presets list
        scroll = ScrollView()
        self.presets_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.presets_layout.bind(minimum_height=self.presets_layout.setter('height'))
        scroll.add_widget(self.presets_layout)
        main_layout.add_widget(scroll)
        
        # Add preset section
        add_preset_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.preset_name_input = TextInput(hint_text='Preset Name', size_hint_x=0.4)
        add_preset_btn = Button(text='Save Current Settings as Preset', size_hint_x=0.6)
        add_preset_btn.bind(on_press=self.save_preset)
        add_preset_layout.add_widget(self.preset_name_input)
        add_preset_layout.add_widget(add_preset_btn)
        main_layout.add_widget(add_preset_layout)
        
        presets_tab.add_widget(main_layout)
        self.main_layout.add_widget(presets_tab)
        
        # Load presets
        self.load_presets_ui()
    
    def create_about_tab(self):
        about_tab = TabbedPanelItem(text='About')
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Title
        title = Label(
            text="Professional Music Generator Studio",
            font_size=28,
            bold=True,
            color=(0.2, 0.8, 1, 1),
            size_hint_y=None,
            height=60
        )
        main_layout.add_widget(title)
        
        # Description
        desc = Label(
            text="Create unique musical compositions with AI-powered generation.\n"
                 "Adjust parameters, generate music, and export to MIDI format.\n"
                 "Real-time visualization and playback included.",
            font_size=16,
            halign='center',
            valign='middle',
            text_size=(None, None)
        )
        main_layout.add_widget(desc)
        
        # Features
        features_header = Label(
            text="Key Features",
            font_size=20,
            bold=True,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(features_header)
        
        features = [
            "• AI-powered music composition",
            "• Real-time audio playback",
            "• Advanced visualization",
            "• MIDI export functionality",
            "• Preset management system",
            "• Multiple chord progressions",
            "• Customizable parameters"
        ]
        
        for feature in features:
            feature_label = Label(
                text=feature,
                font_size=14,
                halign='left'
            )
            main_layout.add_widget(feature_label)
        
        # Version info
        version = Label(
            text="Version 2.1 • Developed with Kivy and Python",
            font_size=12,
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=30
        )
        main_layout.add_widget(version)
        
        about_tab.add_widget(main_layout)
        self.main_layout.add_widget(about_tab)
    
    def load_presets_ui(self):
        self.presets_layout.clear_widgets()
        
        for name, params in self.preset_manager.presets.items():
            preset_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
            
            # Preset info
            info_layout = BoxLayout(orientation='vertical')
            name_label = Label(text=name, font_size=16, bold=True, halign='left')
            params_label = Label(
                text=f"Tempo: {params['tempo']} BPM | Key: {params['key']} {params['scale']} | Sections: {params['sections']}",
                font_size=12,
                color=(0.7, 0.7, 0.7, 1),
                halign='left'
            )
            info_layout.add_widget(name_label)
            info_layout.add_widget(params_label)
            preset_box.add_widget(info_layout)
            
            # Action buttons
            buttons_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=200, spacing=5)
            
            load_btn = Button(text='Load', size_hint_x=None, width=80)
            load_btn.bind(on_press=lambda x, n=name: self.load_preset(n))
            buttons_layout.add_widget(load_btn)
            
            delete_btn = Button(text='Delete', size_hint_x=None, width=80)
            delete_btn.bind(on_press=lambda x, n=name: self.delete_preset(n))
            buttons_layout.add_widget(delete_btn)
            
            preset_box.add_widget(buttons_layout)
            self.presets_layout.add_widget(preset_box)
    
    def load_preset(self, name):
        if name in self.preset_manager.presets:
            params = self.preset_manager.presets[name]
            self.tempo_slider.value = params['tempo']
            self.key_spinner.text = params['key']
            self.scale_spinner.text = params['scale']
            self.sections_slider.value = params['sections']
            self.status_label.text = f"Loaded preset: {name}"
            self.status_label.color = (0.2, 1, 0.2, 1)
    
    def save_preset(self, instance):
        name = self.preset_name_input.text.strip()
        if not name:
            self.status_label.text = "Please enter a preset name"
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
            
        params = {
            'tempo': int(self.tempo_slider.value),
            'key': self.key_spinner.text,
            'scale': self.scale_spinner.text,
            'sections': int(self.sections_slider.value)
        }
        
        self.preset_manager.add_preset(name, params)
        self.load_presets_ui()
        self.preset_name_input.text = ""
        self.status_label.text = f"Saved preset: {name}"
        self.status_label.color = (0.2, 1, 0.2, 1)
    
    def delete_preset(self, name):
        self.preset_manager.delete_preset(name)
        self.load_presets_ui()
        self.status_label.text = f"Deleted preset: {name}"
        self.status_label.color = (1, 1, 0, 1)
    
    def on_tempo_change(self, instance, value):
        self.tempo_value.text = f"{int(value)} BPM"
        self.tempo_display.text = f"Tempo: {int(value)} BPM"
    
    def on_sections_change(self, instance, value):
        self.sections_value.text = str(int(value))
    
    def update_key_display(self):
        scale_names = {'major': 'Major', 'minor': 'Minor', 'pentatonic': 'Pentatonic'}
        self.key_display.text = f"Key: {self.key_spinner.text} {scale_names[self.scale_spinner.text]}"
    
    def generate_composition(self, instance):
        self.status_label.text = "Generating musical composition..."
        self.status_label.color = (1, 1, 0, 1)
        
        # Update generator parameters
        self.generator.tempo = int(self.tempo_slider.value)
        self.generator.key = self.key_spinner.text
        self.generator.scale = self.scale_spinner.text
        sections = int(self.sections_slider.value)
        style = self.style_spinner.text
        
        # Generate composition
        self.generator.compose_song(sections=sections, style=style)
        self.update_key_display()
        
        self.status_label.text = f"Composition ready! Tempo: {self.generator.tempo} BPM | Key: {self.generator.key} {self.generator.scale} | Style: {style}"
        self.status_label.color = (0.2, 1, 0.2, 1)
    
    def toggle_playback(self, instance):
        if not self.generator.composition:
            self.status_label.text = "Please generate a composition first!"
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
            
        if self.generator.is_playing:
            self.generator.stop_playback()
            self.play_btn.text = "▶ Play Composition"
            self.status_label.text = "Playback stopped"
            self.status_label.color = (1, 1, 0, 1)
        else:
            self.play_btn.text = "⏸ Pause Playback"
            self.status_label.text = "Playing composition..."
            self.status_label.color = (0.2, 0.8, 1, 1)
            self.generator.play_composition(
                note_callback=self.visualizer.add_note,
                finished_callback=self.playback_finished
            )
    
    def stop_playback(self, instance):
        self.generator.stop_playback()
        self.play_btn.text = "▶ Play Composition"
        self.status_label.text = "Playback stopped"
        self.status_label.color = (1, 1, 0, 1)
    
    def playback_finished(self):
        self.play_btn.text = "▶ Play Composition"
        self.status_label.text = "Playback finished"
        self.status_label.color = (0.2, 1, 0.2, 1)
    
    def save_midi(self, instance):
        if not self.generator.composition:
            self.status_label.text = "Generate a composition first!"
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
            
        try:
            filename = self.generator.save_midi()
            self.status_label.text = f"Composition saved as '{filename}'"
            self.status_label.color = (0.2, 1, 0.2, 1)
        except Exception as e:
            self.status_label.text = f"Error saving file: {str(e)}"
            self.status_label.color = (1, 0.2, 0.2, 1)
    
    def on_stop(self):
        self.generator.close()

if __name__ == '__main__':
    MusicGeneratorApp().run()