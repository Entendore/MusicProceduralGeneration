# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from app import ProceduralMusicApp
from config import PRESET_FOLDER, EXPORT_FOLDER, DEFAULT_PRESET
from presets import load_preset_file, validate_preset, clone_preset, clone_preset_versioned
from logger import info, error
from themes import DARK_THEME

def ensure_folders():
    """Create necessary folders if they don't exist."""
    os.makedirs(PRESET_FOLDER, exist_ok=True)
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    info(f"Ensured folders exist: {PRESET_FOLDER}, {EXPORT_FOLDER}")

def load_and_validate_default_preset(window: ProceduralMusicApp):
    """Load default preset, validate, and create a versioned backup."""
    if not DEFAULT_PRESET:
        return

    preset_path = os.path.join(PRESET_FOLDER, DEFAULT_PRESET)
    if not os.path.exists(preset_path):
        info(f"Default preset not found: {DEFAULT_PRESET}")
        return

    preset_data = load_preset_file(preset_path)
    if not validate_preset(preset_data):
        info(f"Default preset invalid, skipping load: {DEFAULT_PRESET}")
        return

    # Versioned backup with cleanup (keep last 5)
    try:
        backup_name = clone_preset_versioned(
            preset_path, PRESET_FOLDER, DEFAULT_PRESET, max_versions=5
        )
        info(f"Created versioned backup: {backup_name}")
    except Exception as e:
        error(f"Failed to create versioned backup: {e}")

    # Load preset into app
    window.load_preset(DEFAULT_PRESET)
    info(f"Loaded default preset: {DEFAULT_PRESET}")
    
def main():
    try:
        # Ensure necessary directories
        ensure_folders()

        # Initialize Qt application
        app = QApplication(sys.argv)
        app.setStyleSheet(DARK_THEME)

        # Create main window
        window = ProceduralMusicApp()
        window.resize(800, 900)
        window.show()

        load_and_validate_default_preset(window)

        info("Application started successfully.")
        sys.exit(app.exec())
    except Exception as e:
        error(f"Application failed to start: {e}")
        try:
            QMessageBox.critical(None, "Startup Error", str(e))
        except:
            pass
        raise

if __name__ == "__main__":
    main()
