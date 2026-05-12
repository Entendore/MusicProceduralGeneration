# logger.py
import logging
import sys

# ==============================
# Configure basic logging
# ==============================
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s',
        stream=sys.stdout
    )

# ==============================
# Convenience functions
# ==============================
def info(msg: str):
    """Log an info message"""
    logging.info(msg)

def warn(msg: str):
    """Log a warning message"""
    logging.warning(msg)

def error(msg: str):
    """Log an error message"""
    logging.error(msg)

def debug(msg: str):
    """Log a debug message"""
    logging.debug(msg)

# ==============================
# Optional: Toggle debug mode
# ==============================
def set_debug(enabled: bool = True):
    if enabled:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)