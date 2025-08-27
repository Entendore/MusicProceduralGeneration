# presets.py
import os, json, random

def save_preset_file(filename, values):
    """Save preset values as JSON"""
    if not filename.endswith(".json"):
        filename += ".json"
    with open(filename, "w") as f:
        json.dump(values, f, indent=4)

def load_preset_file(filename):
    """Load preset values from JSON"""
    if not os.path.exists(filename):
        return {}
    with open(filename, "r") as f:
        return json.load(f)

def list_presets(folder):
    """Return all preset files in a folder"""
    return [f for f in os.listdir(folder) if f.endswith(".json")]

def random_preset(scales, instruments):
    """Generate a random preset dictionary"""
    return {
        "tempo": random.randint(40, 160),
        "scale": random.choice(list(scales.keys())),
        "instrument": random.choice(instruments),
        "use_arpeggio": random.choice([True, False]),
        "reverb": random.randint(0, 100),
        "delay": random.randint(0, 100),
        "chorus": random.randint(0, 100),
        "phaser": random.randint(0, 100),
        "stereo_widen": random.randint(0, 100),
        "lowpass": random.randint(5000, 20000),
        "highpass": random.randint(20, 5000),
    }
