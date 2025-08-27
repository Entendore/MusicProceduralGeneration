# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app import ProceduralMusicApp
from config import PRESET_FOLDER, EXPORT_FOLDER
from logger import info
from themes import DARK_THEME

# ==============================
# Ensure necessary folders exist
# ==============================
os.makedirs(PRESET_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# ==============================
# Launch Application
# ==============================
def main():
    # Initialize QApplication
    app = QApplication(sys.argv)

    # Optional: Set global style (dark theme)
    app.setStyleSheet(DARK_THEME)

    # Initialize Main Window
    window = ProceduralMusicApp()
    window.setWindowTitle("Cinematic Procedural Ambient DAW")
    window.resize(800, 900)
    window.show()

    info("Application started successfully.")
    sys.exit(app.exec())

# ==============================
# Entry Point
# ==============================
if __name__ == "__main__":
    main()
