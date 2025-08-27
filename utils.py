# utils.py
import os
import random
from typing import Any, List, Optional
import re


# ==============================
# Folder Utilities
# ==============================
def ensure_folder(path: str):
    """Ensure a folder exists"""
    os.makedirs(path, exist_ok=True)

def list_files(folder: str, extensions: Optional[List[str]] = None, full_path: bool = False, recursive: bool = False) -> List[str]:
    """List files in a folder optionally filtered by extensions."""
    if not os.path.exists(folder):
        return []

    files = []
    if recursive:
        for root, _, filenames in os.walk(folder):
            for f in filenames:
                if extensions is None or any(f.lower().endswith(ext.lower()) for ext in extensions):
                    files.append(os.path.join(root, f) if full_path else f)
    else:
        for f in os.listdir(folder):
            if os.path.isfile(os.path.join(folder, f)) and (extensions is None or any(f.lower().endswith(ext.lower()) for ext in extensions)):
                files.append(os.path.join(folder, f) if full_path else f)
    return files

def safe_list_files(folder: str, extensions: Optional[List[str]] = None, full_path: bool = False, recursive: bool = False) -> List[str]:
    """Ensure folder exists, then list files with optional extensions."""
    if not os.path.exists(folder):
        return []
    from utils import list_files  # reuse existing list_files
    return list_files(folder, extensions=extensions, full_path=full_path, recursive=recursive)

# ==============================
# Random Utilities
# ==============================
def random_choice(choices: List[Any], default: Any = None) -> Any:
    """Return a random element from a list safely"""
    if not choices:
        return default
    return random.choice(choices)

def weighted_choice(choices: List[Any], weights: Optional[List[float]] = None, default: Any = None) -> Any:
    """Randomly choose an item with optional weights"""
    if not choices:
        return default
    return random.choices(choices, weights=weights, k=1)[0]

def random_int(min_val: int, max_val: int) -> int:
    """Return a random integer in range [min_val, max_val]"""
    return random.randint(min_val, max_val)

def random_float(min_val: float, max_val: float) -> float:
    """Return a random float in range [min_val, max_val]"""
    return random.uniform(min_val, max_val)

def random_sample(choices: List[Any], k: int, default: Optional[List[Any]] = None) -> List[Any]:
    """Return a random sample of k elements from a list safely"""
    if not choices or k <= 0:
        return default or []
    return random.sample(choices, min(k, len(choices)))

# ==============================
# Numeric Utilities
# ==============================
def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value to a min/max range"""
    return max(min_val, min(value, max_val))

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by t in [0,1]"""
    return a + (b - a) * clamp(t, 0.0, 1.0)

# ==============================
# Time / String Utilities
# ==============================
def seconds_to_hms(seconds: float, show_ms: bool = False, trim_hours: bool = False) -> str:
    """Convert seconds to HH:MM:SS (optionally with milliseconds)"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    
    if show_ms:
        time_str = f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
    else:
        time_str = f"{h:02d}:{m:02d}:{s:02d}"

    if trim_hours:
        if h == 0:
            time_str = f"{m:02d}:{s:02d}" + (f".{ms:03d}" if show_ms else "")
    return time_str

def humanize_list(items: list[str], conjunction: str = "and") -> str:
    """Convert a list of strings into a human-readable list."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} {conjunction} {items[-1]}"


def safe_filename(name: str, replace_space: bool = True, collapse_underscores: bool = True) -> str:
    """Make a string safe for filenames."""
    safe = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    if replace_space:
        safe = re.sub(r"\s+", "_", safe)
    if collapse_underscores:
        safe = re.sub(r"_+", "_", safe)
    return safe

