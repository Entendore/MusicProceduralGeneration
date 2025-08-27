# ui_controls.py
from PyQt6.QtWidgets import QLabel, QSlider, QCheckBox, QComboBox

def make_slider(label, min_val, max_val, default, orientation, layout):
    layout.addWidget(QLabel(label))
    slider = QSlider(orientation)
    slider.setRange(min_val, max_val)
    slider.setValue(default)
    layout.addWidget(slider)
    return slider

def make_checkbox(label, default, layout):
    box = QCheckBox(label)
    box.setChecked(default)
    layout.addWidget(box)
    return box

def make_combo(label, items, default, layout):
    layout.addWidget(QLabel(label))
    combo = QComboBox()
    combo.addItems(items)
    combo.setCurrentText(default)
    layout.addWidget(combo)
    return combo
