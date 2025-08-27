# main.py
import sys, os
from PyQt6.QtWidgets import QApplication
from app import ProceduralMusicApp
from config import PRESET_FOLDER, EXPORT_FOLDER
from logger import info
from themes import DARK_THEME

os.makedirs(PRESET_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)  # Apply global dark theme

    window = ProceduralMusicApp()
    window.resize(800, 900)
    window.show()

    info("Application started successfully.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
