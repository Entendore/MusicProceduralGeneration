# utils.py
import os
import random
import re
import unicodedata
from pathlib import Path
from typing import Any, List, Optional, Union


# ==============================
# Folder Utilities
# ==============================
def ensure_folder(path: Union[str, Path]):
    """Ensure a folder exists"""
    Path(path).mkdir(parents=True, exist_ok=True)


def list_files(
    folder: Union[str, Path],
    extensions: Optional[List[str]] = None,
    full_path: bool = False,
    recursive: bool = False
) -> List[str]:
    """List files in a folder optionally filtered by extensions."""
    folder_path = Path(folder)
    if not folder_path.exists():
        return []

    files = []
    if recursive:
        for f in folder_path.rglob("*"):
            if f.is_file() and (extensions is None or any(f.name.lower().endswith(ext.lower()) for ext in extensions)):
                files.append(str(f) if full_path else f.name)
    else:
        for f in folder_path.iterdir():
            if f.is_file() and (extensions is None or any(f.name.lower().endswith(ext.lower()) for ext in extensions)):
                files.append(str(f) if full_path else f.name)
    return files


def safe_list_files(
    folder: Union[str, Path],
    extensions: Optional[List[str]] = None,
    full_path: bool = False,
    recursive: bool = False
) -> List[str]:
    """Ensure folder exists, then list files with optional extensions."""
    folder_path = Path(folder)
    if not folder_path.exists():
        return []
    return list_files(folder_path, extensions=extensions, full_path=full_path, recursive=recursive)


# ==============================
# Random Context
# ==============================
class RandomContext:
    """A seedable random context for reproducible randomness."""

    def __init__(self, seed: Optional[int] = None):
        self.random = random.Random(seed)

    def choice(self, choices: List[Any], default: Any = None) -> Any:
        if not choices:
            return default
        return self.random.choice(choices)

    def weighted_choice(self, choices: List[Any], weights: Optional[List[float]] = None, default: Any = None) -> Any:
        if not choices:
            return default
        return self.random.choices(choices, weights=weights, k=1)[0]

    def randint(self, min_val: int, max_val: int) -> int:
        return self.random.randint(min_val, max_val)

    def uniform(self, min_val: float, max_val: float) -> float:
        return self.random.uniform(min_val, max_val)

    def sample(self, choices: List[Any], k: int, default: Optional[List[Any]] = None) -> List[Any]:
        if not choices or k <= 0:
            return default if default is not None else []
        return self.random.sample(choices, min(k, len(choices)))

# ==============================
# Advanced Weighted / Procedural Generators
# ==============================
def weighted_random_list(
    items: List[Any],
    weights: Optional[List[float]] = None,
    count: int = 1,
    rc: Optional[RandomContext] = None
) -> List[Any]:
    """
    Generate a list of randomly selected items based on weights.
    
    Args:
        items: list of items to choose from.
        weights: list of corresponding weights (same length as items).
        count: number of items to select.
        rc: optional RandomContext for reproducibility.
    
    Returns:
        List of selected items.
    """
    if not items or count <= 0:
        return []
    rc_local = rc.random if rc else random
    return rc_local.choices(items, weights=weights, k=count)


def unique_weighted_random_list(
    items: List[Any],
    weights: Optional[List[float]] = None,
    count: int = 1,
    rc: Optional[RandomContext] = None
) -> List[Any]:
    """
    Generate a unique list of randomly selected items based on weights.
    Ensures no duplicates if count <= len(items).
    """
    if not items or count <= 0:
        return []
    rc_local = rc.random if rc else random
    count = min(count, len(items))
    
    if weights is None:
        return rc_local.sample(items, count)
    
    selected = []
    pool = items[:]
    pool_weights = weights[:]
    
    for _ in range(count):
        choice = rc_local.choices(pool, weights=pool_weights, k=1)[0]
        idx = pool.index(choice)
        selected.append(choice)
        del pool[idx]
        del pool_weights[idx]
    
    return selected


def random_distribute(total: float, parts: int, min_val: float = 0.0, max_val: Optional[float] = None, rc: Optional[RandomContext] = None) -> List[float]:
    """
    Randomly distribute a total sum into `parts` numbers, optionally clamped.
    
    Args:
        total: total sum to distribute.
        parts: number of parts to split into.
        min_val: minimum value for each part.
        max_val: maximum value for each part (defaults to total).
        rc: optional RandomContext.
    
    Returns:
        List of floats summing approximately to total (clamped individually if needed).
    """
    max_val = max_val if max_val is not None else total
    rc_local = rc.random if rc else random
    
    values = [rc_local.uniform(min_val, max_val) for _ in range(parts)]
    current_total = sum(values)
    scale = total / current_total if current_total != 0 else 0
    scaled_values = [v * scale for v in values]
    
    # Clamp final values
    return [clamp(v, min_val, max_val) for v in scaled_values]


def random_pattern_from_weights(
    length: int,
    items: List[Any],
    weights: Optional[List[float]] = None,
    rc: Optional[RandomContext] = None
) -> List[Any]:
    """
    Generate a random sequence of items of given length using weights.
    
    Useful for rhythm patterns, note sequences, procedural content.
    """
    return weighted_random_list(items, weights=weights, count=length, rc=rc)


def random_permutation(items: List[Any], rc: Optional[RandomContext] = None) -> List[Any]:
    """
    Return a full random permutation of the list.
    """
    return shuffle_list(items, rc=rc)


def random_boolean_list(length: int, p: float = 0.5, rc: Optional[RandomContext] = None) -> List[bool]:
    """
    Generate a list of True/False values of given length.
    Each True occurs with probability p.
    """
    return [random_bool(p=p, rc=rc) for _ in range(length)]

# ==============================
# Random Utilities (with optional RandomContext)
# ==============================
def random_choice(choices: List[Any], default: Any = None, rc: Optional[RandomContext] = None) -> Any:
    if not choices:
        return default
    if rc:
        return rc.choice(choices, default=default)
    return random.choice(choices)


def weighted_choice(choices: List[Any], weights: Optional[List[float]] = None, default: Any = None, rc: Optional[RandomContext] = None) -> Any:
    if not choices:
        return default
    if rc:
        return rc.weighted_choice(choices, weights=weights, default=default)
    return random.choices(choices, weights=weights, k=1)[0]


def random_int(min_val: int, max_val: int, rc: Optional[RandomContext] = None) -> int:
    if rc:
        return rc.randint(min_val, max_val)
    return random.randint(min_val, max_val)


def random_float(min_val: float, max_val: float, rc: Optional[RandomContext] = None) -> float:
    if rc:
        return rc.uniform(min_val, max_val)
    return random.uniform(min_val, max_val)


def random_sample(choices: List[Any], k: int, default: Optional[List[Any]] = None, rc: Optional[RandomContext] = None) -> List[Any]:
    if not choices or k <= 0:
        return default if default is not None else []
    if rc:
        return rc.sample(choices, k, default=default)
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

def remap(value: float, old_min: float, old_max: float, new_min: float, new_max: float) -> float:
    """Remap a value from one range to another."""
    t = (value - old_min) / (old_max - old_min)
    return lerp(new_min, new_max, t)

# ==============================
# Time / String Utilities
# ==============================
def seconds_to_hms(seconds: float, show_ms: bool = False, trim_hours: bool = False) -> str:
    """Convert seconds to HH:MM:SS (optionally with milliseconds)"""
    seconds = max(0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)

    if show_ms:
        time_str = f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
    else:
        time_str = f"{h:02d}:{m:02d}:{s:02d}"

    if trim_hours and h == 0:
        time_str = f"{m:02d}:{s:02d}" + (f".{ms:03d}" if show_ms else "")
    return time_str


def humanize_list(items: List[str], conjunction: str = "and", oxford_comma: bool = True) -> str:
    """Convert a list of strings into a human-readable list."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if oxford_comma and len(items) > 2:
        return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"
    return f"{', '.join(items[:-1])} {conjunction} {items[-1]}"


def safe_filename(name: str, replace_space: bool = True, collapse_underscores: bool = True) -> str:
    """Make a string safe for filenames."""
    # Normalize Unicode
    safe = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    # Keep only allowed characters
    safe = "".join(c for c in safe if c.isalnum() or c in (' ', '-', '_')).rstrip()
    if replace_space:
        safe = re.sub(r"\s+", "_", safe)
    if collapse_underscores:
        safe = re.sub(r"_+", "_", safe)
    return safe
