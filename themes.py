# themes.py

# ==============================
# Dark Theme (Modern Ambient Look)
# ==============================
DARK_THEME = """
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12pt;
}

QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    padding: 5px 10px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #3d3d3d;
}
QPushButton:checked {
    background-color: #5a5a5a;
}

QSlider::groove:horizontal {
    border: 1px solid #444444;
    height: 8px;
    background: #2d2d2d;
    margin: 2px 0;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #5a5a5a;
    border: 1px solid #777777;
    width: 18px;
    margin: -4px 0;
    border-radius: 9px;
}

QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    padding: 3px 5px;
    border-radius: 4px;
}
QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    selection-background-color: #5a5a5a;
    color: #ffffff;
}

QCheckBox {
    spacing: 5px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
}
QCheckBox::indicator:unchecked {
    border: 1px solid #777777;
    background: #2d2d2d;
}
QCheckBox::indicator:checked {
    border: 1px solid #777777;
    background: #5a5a5a;
}

QLabel {
    font-weight: bold;
}

"""

# ==============================
# Light Theme (Optional)
# ==============================
LIGHT_THEME = """
QWidget {
    background-color: #f0f0f0;
    color: #000000;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12pt;
}

QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #aaaaaa;
    padding: 5px 10px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #d0d0d0;
}
QPushButton:checked {
    background-color: #b0b0b0;
}

QSlider::groove:horizontal {
    border: 1px solid #aaaaaa;
    height: 8px;
    background: #e0e0e0;
    margin: 2px 0;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #b0b0b0;
    border: 1px solid #888888;
    width: 18px;
    margin: -4px 0;
    border-radius: 9px;
}

QComboBox {
    background-color: #e0e0e0;
    border: 1px solid #aaaaaa;
    padding: 3px 5px;
    border-radius: 4px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    selection-background-color: #b0b0b0;
    color: #000000;
}

QCheckBox {
    spacing: 5px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
}
QCheckBox::indicator:unchecked {
    border: 1px solid #888888;
    background: #e0e0e0;
}
QCheckBox::indicator:checked {
    border: 1px solid #888888;
    background: #b0b0b0;
}

QLabel {
    font-weight: bold;
}
"""
