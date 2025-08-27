# utils.py
import os
import random
from typing import Any, List, Optional

# ==============================
# Folder Utilities
# ==============================
def ensure_folder(path: str):
    """Ensure a folder exists"""
    if not os.path.exists(path):
        os.makedirs(path)

def list_files(folder: str, extensions: Optional[List[str]] = None) -> List[str]:
    """List files in a folder optionally filtered by extensions"""
    if not os.path.exists(folder):
        return []
    files = os.listdir(folder)
    if extensions:
        files = [f for f in files if any(f.lower().endswith(ext.lower()) for ext in extensions)]
    return files

# ==============================
# Random Utilities
# ==============================
def random_choice(choices: List[Any]) -> Any:
    """Return a random element from a list safely"""
    if not choices:
        return None
    return random.choice(choices)

def random_int(min_val: int, max_val: int) -> int:
    """Return a random integer in range [min_val, max_val]"""
    return random.randint(min_val, max_val)

def random_float(min_val: float, max_val: float) -> float:
    """Return a random float in range [min_val, max_val]"""
    return random.uniform(min_val, max_val)

# ==============================
# Numeric Utilities
# ==============================
def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value to a min/max range"""
    return max(min_val, min(value, max_val))

# ==============================
# Time / String Utilities
# ==============================
def seconds_to_hms(seconds: float) -> str:
    """Convert seconds to HH:MM:SS string"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def safe_filename(name: str) -> str:
    """Make a string safe for filenames"""
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
