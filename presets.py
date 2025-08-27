# presets.py
import os
import json
import shutil
import re
import random
from typing import Dict, List, Optional
import config

REQUIRED_PRESET_KEYS = config.REQUIRED_PRESETS_KEYS

def clone_preset(src_filename: str, dest_filename: str) -> bool:
    """Copy an existing preset file to a new filename safely."""
    if not os.path.exists(src_filename):
        return False
    if not dest_filename.endswith(".json"):
        dest_filename += ".json"
    shutil.copy(src_filename, dest_filename)
    return True

def clone_preset_versioned(src_filename: str, folder: str, base_name: str) -> str:
    """
    Clone a preset with automatic versioning.
    Example: "MyPreset.json" -> "MyPreset_v1.json", "MyPreset_v2.json", ...
    Returns the new backup filename.
    """
    if not os.path.exists(src_filename):
        raise FileNotFoundError(f"Source preset not found: {src_filename}")

    # Ensure .json extension
    if not base_name.endswith(".json"):
        base_name += ".json"

    # Find existing versions
    name_only = base_name.replace(".json", "")
    pattern = re.compile(rf"{re.escape(name_only)}_v(\d+)\.json")
    existing_versions = [
        f for f in os.listdir(folder) if pattern.match(f)
    ]
    
    if existing_versions:
        # Determine next version number
        version_numbers = [int(pattern.match(f).group(1)) for f in existing_versions]
        next_version = max(version_numbers) + 1
    else:
        next_version = 1

    new_name = f"{name_only}_v{next_version}.json"
    new_path = os.path.join(folder, new_name)
    shutil.copy(src_filename, new_path)
    return new_name

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


def list_presets(folder: str) -> List[str]:
    """Return all preset files in a folder"""
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if f.endswith(".json")]

def validate_preset(preset: Dict) -> bool:
    """Check if a preset dictionary contains all required keys."""
    return all(key in preset for key in REQUIRED_PRESET_KEYS)

def random_preset(scales: Dict, instruments: List[str], tempo_range=(40, 160)) -> Dict:
    """Generate a random preset dictionary"""
    import random
    return {
        "tempo": random.randint(*tempo_range),
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
