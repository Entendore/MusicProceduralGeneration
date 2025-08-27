# utils.py
import os
import random
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable, List, Optional, Union

# ==============================
# Folder Utilities
# ==============================
def ensure_folder(path: Union[str, Path]):
    """Ensure a folder exists."""
    Path(path).mkdir(parents=True, exist_ok=True)

def list_files(
    folder: Union[str, Path],
    extensions: Optional[List[str]] = None,
    full_path: bool = False,
    recursive: bool = False,
    ignore_hidden: bool = True
) -> List[str]:
    """List files in a folder, optionally filtered by extensions and ignoring hidden files."""
    folder_path = Path(folder)
    if not folder_path.exists():
        return []

    files = []
    iterator = folder_path.rglob("*") if recursive else folder_path.iterdir()
    for f in iterator:
        if f.is_file():
            if ignore_hidden and f.name.startswith('.'):
                continue
            if extensions is None or any(f.name.lower().endswith(ext.lower()) for ext in extensions):
                files.append(str(f) if full_path else f.name)
    return files

def safe_list_files(
    folder: Union[str, Path],
    extensions: Optional[List[str]] = None,
    full_path: bool = False,
    recursive: bool = False,
    ignore_hidden: bool = True
) -> List[str]:
    """Ensure folder exists, then list files with optional extensions."""
    ensure_folder(folder)
    return list_files(folder, extensions=extensions, full_path=full_path, recursive=recursive, ignore_hidden=ignore_hidden)

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

    def randrange(self, start: int, stop: int, step: int = 1) -> int:
        return self.random.randrange(start, stop, step)

    def uniform(self, min_val: float, max_val: float) -> float:
        return self.random.uniform(min_val, max_val)

    def sample(self, choices: List[Any], k: int, default: Optional[List[Any]] = None) -> List[Any]:
        if not choices or k <= 0:
            return default if default is not None else []
        return self.random.sample(choices, min(k, len(choices)))

    def shuffle(self, items: List[Any]) -> List[Any]:
        copy = items[:]
        self.random.shuffle(copy)
        return copy

# ==============================
# Random Utilities
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
    return rc.randint(min_val, max_val) if rc else random.randint(min_val, max_val)

def random_float(min_val: float, max_val: float, rc: Optional[RandomContext] = None) -> float:
    return rc.uniform(min_val, max_val) if rc else random.uniform(min_val, max_val)

def random_sample(choices: List[Any], k: int, default: Optional[List[Any]] = None, rc: Optional[RandomContext] = None) -> List[Any]:
    if not choices or k <= 0:
        return default if default is not None else []
    return rc.sample(choices, k, default=default) if rc else random.sample(choices, min(k, len(choices)))

def shuffle_list(items: List[Any], rc: Optional[RandomContext] = None) -> List[Any]:
    items_copy = items[:]
    if rc:
        rc.random.shuffle(items_copy)
    else:
        random.shuffle(items_copy)
    return items_copy

def random_bool(p: float = 0.5, rc: Optional[RandomContext] = None) -> bool:
    r = rc.random.random() if rc else random.random()
    return r < p

# ==============================
# Numeric Utilities
# ==============================
def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * clamp(t, 0.0, 1.0)

def remap(value: float, old_min: float, old_max: float, new_min: float, new_max: float) -> float:
    t = (value - old_min) / (old_max - old_min) if old_max != old_min else 0
    return lerp(new_min, new_max, t)

def map_list(values: List[float], old_min: float, old_max: float, new_min: float, new_max: float) -> List[float]:
    return [remap(v, old_min, old_max, new_min, new_max) for v in values]

# ==============================
# Time / String Utilities
# ==============================
def seconds_to_hms(seconds: float, show_ms: bool = False, trim_hours: bool = False) -> str:
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

def humanize_list(items: Iterable[str], conjunction: Optional[str] = "and", oxford_comma: bool = True) -> str:
    items = list(items)
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if conjunction is None:
        return ", ".join(items)
    if oxford_comma and len(items) > 2:
        return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"
    return f"{', '.join(items[:-1])} {conjunction} {items[-1]}"

def safe_filename(name: str, max_length: int = 255, replace_space: bool = True, collapse_underscores: bool = True) -> str:
    safe = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    safe = "".join(c for c in safe if c.isalnum() or c in (' ', '-', '_')).rstrip()
    if replace_space:
        safe = re.sub(r"\s+", "_", safe)
    if collapse_underscores:
        safe = re.sub(r"_+", "_", safe)
    return safe[:max_length]

# ==============================
# Procedural Random Toolkit
# ==============================
def random_sign(rc: Optional[RandomContext] = None) -> int:
    return -1 if random_bool(0.5, rc=rc) else 1

def random_range_list(length: int, min_val: float, max_val: float, rc: Optional[RandomContext] = None) -> List[float]:
    return [random_float(min_val, max_val, rc=rc) for _ in range(length)]

def weighted_random_list(items: List[Any], weights: Optional[List[float]] = None, count: int = 1, rc: Optional[RandomContext] = None) -> List[Any]:
    if not items or count <= 0:
        return []
    rc_local = rc.random if rc else random
    return rc_local.choices(items, weights=weights, k=count)

def unique_weighted_random_list(items: List[Any], weights: Optional[List[float]] = None, count: int = 1, rc: Optional[RandomContext] = None) -> List[Any]:
    if not items or count <= 0:
        return []
    rc_local = rc.random if rc else random
    count = min(count, len(items))
    if weights is None:
        return rc_local.sample(items, count)
    pool_items, pool_weights = zip(*[(i, w) for i, w in zip(items, weights) if w > 0]) if any(w > 0 for w in weights) else (items, None)
    pool_items = list(pool_items)
    pool_weights = list(pool_weights) if pool_weights is not None else None
    selected = []
    for _ in range(count):
        choice = rc_local.choices(pool_items, weights=pool_weights, k=1)[0]
        idx = pool_items.index(choice)
        selected.append(choice)
        del pool_items[idx]
        if pool_weights:
            del pool_weights[idx]
    return selected

def weighted_shuffle(items: List[Any], weights: Optional[List[float]] = None, rc: Optional[RandomContext] = None, unique: bool = False) -> List[Any]:
    if not items:
        return []
    if unique:
        return unique_weighted_random_list(items, weights=weights, count=len(items), rc=rc)
    rc_local = rc.random if rc else random
    return [rc_local.choices(items, weights=weights, k=1)[0] for _ in range(len(items))]

def random_permutation(items: List[Any], rc: Optional[RandomContext] = None) -> List[Any]:
    return shuffle_list(items, rc=rc)

def random_pattern_from_weights(length: int, items: List[Any], weights: Optional[List[float]] = None, rc: Optional[RandomContext] = None) -> List[Any]:
    return weighted_random_list(items, weights=weights, count=length, rc=rc)

def random_distribute(total: float, parts: int, min_val: float = 0.0, max_val: Optional[float] = None, rc: Optional[RandomContext] = None, adjust_sum: bool = True) -> List[float]:
    max_val = max_val if max_val is not None else total
    rc_local = rc.random if rc else random
    values = [rc_local.uniform(min_val, max_val) for _ in range(parts)]
    current_total = sum(values)
    scaled_values = [v * (total / current_total) for v in values] if current_total != 0 else [total / parts] * parts
    clamped_values = [clamp(v, min_val, max_val) for v in scaled_values]
    if adjust_sum:
        clamped_sum = sum(clamped_values)
        if clamped_sum != 0:
            final_scale = total / clamped_sum
            clamped_values = [v * final_scale for v in clamped_values]
        else:
            clamped_values = [total / parts] * parts
    return clamped_values
