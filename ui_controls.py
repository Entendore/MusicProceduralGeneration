# ui_controls.py
from PyQt6.QtWidgets import (
    QLabel, QSlider, QCheckBox, QComboBox, QSpinBox, QPushButton,
    QLayout, QWidget, QGroupBox, QFrame, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from typing import Optional, Union, Tuple


def style_control(widget: QWidget) -> QWidget:
    """Apply consistent styling to controls (can be expanded later)."""
    widget.setMinimumWidth(120)
    return widget


def make_slider(
    label: str,
    min_val: int,
    max_val: int,
    default: int,
    orientation: Qt.Orientation,
    layout: QLayout,
    tooltip: Optional[str] = None,
    return_label: bool = False,
    link_value_label: Optional[QLabel] = None
) -> Union[QSlider, Tuple[QSlider, QLabel]]:
    """
    Create a slider with label.
    - return_label: if True, returns (slider, label).
    - link_value_label: optional QLabel to auto-update with slider value.
    """
    lbl = QLabel(label)
    layout.addWidget(lbl)

    slider = QSlider(orientation)
    slider.setRange(min_val, max_val)
    slider.setValue(default)
    if tooltip:
        slider.setToolTip(tooltip)

    if link_value_label:
        link_value_label.setText(str(default))
        slider.valueChanged.connect(lambda v: link_value_label.setText(str(v)))

    layout.addWidget(style_control(slider))
    return (slider, lbl) if return_label else slider


def make_checkbox(
    label: str,
    default: bool,
    layout: QLayout,
    tooltip: Optional[str] = None
) -> QCheckBox:
    """Create a checkbox with default state and optional tooltip."""
    box = QCheckBox(label)
    box.setChecked(default)
    if tooltip:
        box.setToolTip(tooltip)
    layout.addWidget(style_control(box))
    return box


def make_combo(
    label: str,
    items: list[str],
    default: str,
    layout: QLayout,
    tooltip: Optional[str] = None,
    return_label: bool = False
) -> Union[QComboBox, Tuple[QComboBox, QLabel]]:
    """Create a combo box with label."""
    lbl = QLabel(label)
    layout.addWidget(lbl)

    combo = QComboBox()
    combo.addItems(items)
    if default in items:
        combo.setCurrentText(default)
    if tooltip:
        combo.setToolTip(tooltip)

    layout.addWidget(style_control(combo))
    return (combo, lbl) if return_label else combo


def make_spinbox(
    label: str,
    min_val: int,
    max_val: int,
    default: int,
    layout: QLayout,
    tooltip: Optional[str] = None,
    step: int = 1,
    return_label: bool = False,
    link_value_label: Optional[QLabel] = None
) -> Union[QSpinBox, Tuple[QSpinBox, QLabel]]:
    """
    Create a numeric spinbox with label.
    - return_label: if True, returns (spinbox, label).
    - link_value_label: optional QLabel to auto-update with spinbox value.
    """
    lbl = QLabel(label)
    layout.addWidget(lbl)

    spin = QSpinBox()
    spin.setRange(min_val, max_val)
    spin.setValue(default)
    spin.setSingleStep(step)
    if tooltip:
        spin.setToolTip(tooltip)

    if link_value_label:
        link_value_label.setText(str(default))
        spin.valueChanged.connect(lambda v: link_value_label.setText(str(v)))

    layout.addWidget(style_control(spin))
    return (spin, lbl) if return_label else spin


def make_button(
    label: str,
    layout: QLayout,
    tooltip: Optional[str] = None,
    checkable: bool = False
) -> QPushButton:
    """Create a button (optionally checkable)."""
    btn = QPushButton(label)
    btn.setCheckable(checkable)
    if tooltip:
        btn.setToolTip(tooltip)

    layout.addWidget(style_control(btn))
    return btn


def make_groupbox(
    title: str,
    layout: QLayout,
    orientation: str = "vertical"
) -> Tuple[QGroupBox, QLayout]:
    """
    Create a group box with its own inner layout.
    Returns (groupbox, inner_layout).
    """
    group = QGroupBox(title)
    inner_layout = QVBoxLayout() if orientation == "vertical" else QHBoxLayout()
    group.setLayout(inner_layout)
    layout.addWidget(group)
    return group, inner_layout


def make_frame(
    layout: QLayout,
    orientation: str = "vertical",
    frame_shape: QFrame.Shape = QFrame.Shape.StyledPanel,
    frame_shadow: QFrame.Shadow = QFrame.Shadow.Raised
) -> Tuple[QFrame, QLayout]:
    """
    Create a styled frame with its own inner layout.
    Returns (frame, inner_layout).
    """
    frame = QFrame()
    frame.setFrameShape(frame_shape)
    frame.setFrameShadow(frame_shadow)
    inner_layout = QVBoxLayout() if orientation == "vertical" else QHBoxLayout()
    frame.setLayout(inner_layout)
    layout.addWidget(frame)
    return frame, inner_layout


def make_label_value(
    label: str,
    default: str,
    layout: QLayout,
    tooltip: Optional[str] = None,
    orientation: str = "horizontal"
) -> Tuple[QLabel, QLabel]:
    """
    Create a (label, value) pair side by side (or stacked).
    - Returns (label_widget, value_widget).
    - Use value_widget.setText() or link via make_slider/make_spinbox.
    """
    container = QFrame()
    inner_layout = QHBoxLayout() if orientation == "horizontal" else QVBoxLayout()
    container.setLayout(inner_layout)

    lbl = QLabel(label)
    val = QLabel(default)

    if tooltip:
        lbl.setToolTip(tooltip)
        val.setToolTip(tooltip)

    inner_layout.addWidget(lbl)
    inner_layout.addWidget(val)
    layout.addWidget(container)

    return lbl, val

def bind_slider_spinbox(slider: QSlider, spinbox: QSpinBox, value_label: Optional[QLabel] = None):
    """
    Bind a slider and spinbox together so they stay in sync.
    Optionally, link a QLabel to show the current value.
    """
    # Update spinbox when slider changes
    slider.valueChanged.connect(lambda v: spinbox.setValue(v))

    # Update slider when spinbox changes
    spinbox.valueChanged.connect(lambda v: slider.setValue(v))

    # Update value label if provided
    if value_label:
        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))

def make_synced_slider(
    label: str,
    min_val: int,
    max_val: int,
    default: int,
    layout: QLayout,
    tooltip: Optional[str] = None,
    orientation: Qt.Orientation = Qt.Orientation.Horizontal,
    show_value_label: bool = True,
    step: int = 1
) -> Tuple[QSlider, QSpinBox, Optional[QLabel]]:
    """
    Create a fully synced slider + spinbox + optional value label.
    Returns (slider, spinbox, value_label).
    """
    container = QFrame()
    inner_layout = QHBoxLayout()
    container.setLayout(inner_layout)
    layout.addWidget(container)

    # Slider
    slider = QSlider(orientation)
    slider.setRange(min_val, max_val)
    slider.setValue(default)
    if tooltip:
        slider.setToolTip(tooltip)
    inner_layout.addWidget(style_control(slider))

    # Spinbox
    spinbox = QSpinBox()
    spinbox.setRange(min_val, max_val)
    spinbox.setValue(default)
    spinbox.setSingleStep(step)
    if tooltip:
        spinbox.setToolTip(tooltip)
    inner_layout.addWidget(style_control(spinbox))

    # Optional value label
    value_label = QLabel(str(default)) if show_value_label else None
    if value_label:
        inner_layout.addWidget(value_label)
        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))

    # Bind slider and spinbox
    slider.valueChanged.connect(spinbox.setValue)
    spinbox.valueChanged.connect(slider.setValue)

    # Optional label for the control
    lbl = QLabel(label)
    layout.addWidget(lbl)

    return slider, spinbox, value_label

def make_synced_slider_float(
    label: str,
    min_val: float,
    max_val: float,
    default: float,
    layout: QLayout,
    tooltip: Optional[str] = None,
    orientation: Qt.Orientation = Qt.Orientation.Horizontal,
    decimals: int = 2,
    show_value_label: bool = True,
    step: float = 0.1
) -> Tuple[QSlider, QDoubleSpinBox, Optional[QLabel]]:
    """
    Create a fully synced slider + QDoubleSpinBox + optional value label for float values.
    Returns (slider, spinbox, value_label).
    """
    from PyQt6.QtWidgets import QDoubleSpinBox

    # Internal multiplier to convert float to int for the slider
    factor = 10 ** decimals
    int_min = int(min_val * factor)
    int_max = int(max_val * factor)
    int_default = int(default * factor)
    int_step = max(1, int(step * factor))

    container = QFrame()
    inner_layout = QHBoxLayout()
    container.setLayout(inner_layout)
    layout.addWidget(container)

    # Slider (integer internally)
    slider = QSlider(orientation)
    slider.setRange(int_min, int_max)
    slider.setValue(int_default)
    if tooltip:
        slider.setToolTip(tooltip)
    inner_layout.addWidget(style_control(slider))

    # QDoubleSpinBox
    spinbox = QDoubleSpinBox()
    spinbox.setDecimals(decimals)
    spinbox.setRange(min_val, max_val)
    spinbox.setSingleStep(step)
    spinbox.setValue(default)
    if tooltip:
        spinbox.setToolTip(tooltip)
    inner_layout.addWidget(style_control(spinbox))

    # Optional value label
    value_label = QLabel(f"{default:.{decimals}f}") if show_value_label else None
    if value_label:
        inner_layout.addWidget(value_label)

    # Binding slider ↔ spinbox
    def slider_to_spin(v: int):
        val = v / factor
        spinbox.blockSignals(True)
        spinbox.setValue(val)
        spinbox.blockSignals(False)
        if value_label:
            value_label.setText(f"{val:.{decimals}f}")

    def spin_to_slider(v: float):
        s = int(round(v * factor))
        slider.blockSignals(True)
        slider.setValue(s)
        slider.blockSignals(False)
        if value_label:
            value_label.setText(f"{v:.{decimals}f}")

    slider.valueChanged.connect(slider_to_spin)
    spinbox.valueChanged.connect(spin_to_slider)

    # Optional label for the control
    lbl = QLabel(label)
    layout.addWidget(lbl)

    return slider, spinbox, value_label

def bind_controls(
    controls: list[Union[QSlider, QSpinBox, 'QDoubleSpinBox']],
    value_labels: Optional[list[QLabel]] = None,
    factor: Optional[list[float]] = None
):
    """
    Bind multiple controls together so they stay in sync.
    - controls: list of sliders/spinboxes to bind.
    - value_labels: optional list of QLabel to update for each control.
    - factor: optional list of multipliers for float-integer conversions (e.g., slider-to-float).
    
    Example: bind_controls([slider1, spin1], [label1])
    """
    if value_labels is None:
        value_labels = [None] * len(controls)
    if factor is None:
        factor = [1.0] * len(controls)

    def make_callback(idx: int):
        def callback(value):
            for j, ctrl in enumerate(controls):
                if j != idx:
                    if isinstance(ctrl, QSlider):
                        val = int(round(value * factor[idx] / factor[j]))
                        ctrl.blockSignals(True)
                        ctrl.setValue(val)
                        ctrl.blockSignals(False)
                    else:  # SpinBox or DoubleSpinBox
                        val = value * factor[idx] / factor[j]
                        ctrl.blockSignals(True)
                        ctrl.setValue(val)
                        ctrl.blockSignals(False)
            # Update value label if provided
            lbl = value_labels[idx]
            if lbl:
                lbl.setText(str(value))
        return callback

    for i, ctrl in enumerate(controls):
        ctrl.valueChanged.connect(make_callback(i))
