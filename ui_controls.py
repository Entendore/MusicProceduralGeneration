# ui_controls.py
from PyQt6.QtWidgets import (
    QLabel, QSlider, QSpinBox, QDoubleSpinBox, QPushButton, QWidget,
    QCheckBox, QComboBox, QLayout, QFrame, QGroupBox, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from typing import Optional, Tuple, List, Union

def make_slider(label: str, min_val: int, max_val: int, default: int,
                orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                parent_layout: Optional[QLayout] = None,
                tooltip: Optional[str] = None,
                link_value_label: Optional[QLabel] = None) -> QSlider:
    """Create a labeled slider with optional value display."""
    layout = QVBoxLayout() if orientation == Qt.Orientation.Horizontal else QHBoxLayout()
    
    lbl = QLabel(label)
    if tooltip:
        lbl.setToolTip(tooltip)
    layout.addWidget(lbl)
    
    slider = QSlider(orientation)
    slider.setMinimum(min_val)
    slider.setMaximum(max_val)
    slider.setValue(default)
    
    if tooltip:
        slider.setToolTip(tooltip)
        
    layout.addWidget(slider)
    
    if link_value_label:
        value_lbl = link_value_label
    else:
        value_lbl = QLabel(str(default))
        layout.addWidget(value_lbl)
    
    # Connect slider to update value label
    def update_value(value):
        value_lbl.setText(str(value))
    
    slider.valueChanged.connect(update_value)
    
    if parent_layout:
        parent_layout.addLayout(layout)
        
    return slider

def make_spinbox(label: str, min_val: int, max_val: int, default: int,
                 parent_layout: Optional[QLayout] = None,
                 tooltip: Optional[str] = None, step: int = 1,
                 link_value_label: Optional[QLabel] = None) -> QSpinBox:
    """Create a labeled spinbox with optional value display."""
    layout = QHBoxLayout()
    
    lbl = QLabel(label)
    if tooltip:
        lbl.setToolTip(tooltip)
    layout.addWidget(lbl)
    
    spinbox = QSpinBox()
    spinbox.setMinimum(min_val)
    spinbox.setMaximum(max_val)
    spinbox.setValue(default)
    spinbox.setSingleStep(step)
    
    if tooltip:
        spinbox.setToolTip(tooltip)
        
    layout.addWidget(spinbox)
    
    if link_value_label:
        value_lbl = link_value_label
        layout.addWidget(value_lbl)
    
    if parent_layout:
        parent_layout.addLayout(layout)
        
    return spinbox

def make_button(label: str, parent_layout: Optional[QLayout] = None,
                tooltip: Optional[str] = None, checkable: bool = False) -> QPushButton:
    """Create a button with optional tooltip."""
    btn = QPushButton(label)
    
    if tooltip:
        btn.setToolTip(tooltip)
        
    btn.setCheckable(checkable)
    
    if parent_layout:
        parent_layout.addWidget(btn)
        
    return btn

def make_checkbox(label: str, default: bool = False,
                  parent_layout: Optional[QLayout] = None,
                  tooltip: Optional[str] = None) -> QCheckBox:
    """Create a checkbox with optional tooltip."""
    checkbox = QCheckBox(label)
    checkbox.setChecked(default)
    
    if tooltip:
        checkbox.setToolTip(tooltip)
        
    if parent_layout:
        parent_layout.addWidget(checkbox)
        
    return checkbox

def make_combo(label: str, items: List[str], default: str,
               parent_layout: Optional[QLayout] = None,
               tooltip: Optional[str] = None) -> QComboBox:
    """Create a labeled combobox."""
    layout = QHBoxLayout()
    
    lbl = QLabel(label)
    if tooltip:
        lbl.setToolTip(tooltip)
    layout.addWidget(lbl)
    
    combo = QComboBox()
    combo.addItems(items)
    combo.setCurrentText(default)
    
    if tooltip:
        combo.setToolTip(tooltip)
        
    layout.addWidget(combo)
    
    if parent_layout:
        parent_layout.addLayout(layout)
        
    return combo

def make_label_value(label: str, default: str = "",
                     parent_layout: Optional[QLayout] = None,
                     tooltip: Optional[str] = None,
                     orientation: str = "horizontal") -> Tuple[QLabel, QLabel]:
    """Create a label with a value display."""
    if orientation == "horizontal":
        layout = QHBoxLayout()
    else:
        layout = QVBoxLayout()
    
    lbl = QLabel(label)
    if tooltip:
        lbl.setToolTip(tooltip)
    layout.addWidget(lbl)
    
    value_lbl = QLabel(default)
    layout.addWidget(value_lbl)
    
    if parent_layout:
        parent_layout.addLayout(layout)
        
    return lbl, value_lbl

def make_groupbox(title: str, parent_layout: Optional[QLayout] = None,
                  orientation: str = "vertical") -> Tuple[QGroupBox, QLayout]:
    """Create a groupbox with a layout."""
    group = QGroupBox(title)
    
    if orientation == "vertical":
        layout = QVBoxLayout()
    else:
        layout = QHBoxLayout()
        
    group.setLayout(layout)
    
    if parent_layout:
        parent_layout.addWidget(group)
        
    return group, layout

def make_frame(parent_layout: Optional[QLayout] = None,
               orientation: str = "vertical",
               frame_shape: QFrame.Shape = QFrame.Shape.StyledPanel,
               frame_shadow: QFrame.Shadow = QFrame.Shadow.Raised) -> Tuple[QFrame, QLayout]:
    """Create a frame with a layout."""
    frame = QFrame()
    frame.setFrameShape(frame_shape)
    frame.setFrameShadow(frame_shadow)
    
    if orientation == "vertical":
        layout = QVBoxLayout()
    else:
        layout = QHBoxLayout()
        
    frame.setLayout(layout)
    
    if parent_layout:
        parent_layout.addWidget(frame)
        
    return frame, layout

def make_synced_slider(label: str, min_val: int, max_val: int, default: int,
                       parent_layout: Optional[QLayout] = None,
                       tooltip: Optional[str] = None,
                       show_value_label: bool = True, step: int = 1) -> Tuple[QSlider, QSpinBox, Optional[QLabel]]:
    """Create a slider and spinbox that stay in sync."""
    layout = QHBoxLayout()
    
    lbl = QLabel(label)
    if tooltip:
        lbl.setToolTip(tooltip)
    layout.addWidget(lbl)
    
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(min_val)
    slider.setMaximum(max_val)
    slider.setValue(default)
    
    if tooltip:
        slider.setToolTip(tooltip)
        
    layout.addWidget(slider)
    
    spinbox = QSpinBox()
    spinbox.setMinimum(min_val)
    spinbox.setMaximum(max_val)
    spinbox.setValue(default)
    spinbox.setSingleStep(step)
    
    if tooltip:
        spinbox.setToolTip(tooltip)
        
    layout.addWidget(spinbox)
    
    value_lbl = None
    if show_value_label:
        value_lbl = QLabel(str(default))
        layout.addWidget(value_lbl)
    
    # Connect slider and spinbox to keep in sync
    def slider_changed(value):
        spinbox.setValue(value)
        if value_lbl:
            value_lbl.setText(str(value))
    
    def spinbox_changed(value):
        slider.setValue(value)
        if value_lbl:
            value_lbl.setText(str(value))
    
    slider.valueChanged.connect(slider_changed)
    spinbox.valueChanged.connect(spinbox_changed)
    
    if parent_layout:
        parent_layout.addLayout(layout)
        
    return slider, spinbox, value_lbl

def make_synced_slider_float(label: str, min_val: float, max_val: float, default: float,
                             parent_layout: Optional[QLayout] = None,
                             tooltip: Optional[str] = None,
                             decimals: int = 2, show_value_label: bool = True, step: float = 0.1
                             ) -> Tuple[QSlider, QDoubleSpinBox, Optional[QLabel]]:
    """Create a slider and double spinbox that stay in sync for float values."""
    layout = QHBoxLayout()
    
    lbl = QLabel(label)
    if tooltip:
        lbl.setToolTip(tooltip)
    layout.addWidget(lbl)
    
    # Convert float range to integers for slider
    factor = 10 ** decimals
    int_min = int(min_val * factor)
    int_max = int(max_val * factor)
    int_default = int(default * factor)
    
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(int_min)
    slider.setMaximum(int_max)
    slider.setValue(int_default)
    
    if tooltip:
        slider.setToolTip(tooltip)
        
    layout.addWidget(slider)
    
    spinbox = QDoubleSpinBox()
    spinbox.setMinimum(min_val)
    spinbox.setMaximum(max_val)
    spinbox.setValue(default)
    spinbox.setSingleStep(step)
    spinbox.setDecimals(decimals)
    
    if tooltip:
        spinbox.setToolTip(tooltip)
        
    layout.addWidget(spinbox)
    
    value_lbl = None
    if show_value_label:
        value_lbl = QLabel(str(default))
        layout.addWidget(value_lbl)
    
    # Connect slider and spinbox to keep in sync
    def slider_changed(value):
        float_value = value / factor
        spinbox.setValue(float_value)
        if value_lbl:
            value_lbl.setText(f"{float_value:.{decimals}f}")
    
    def spinbox_changed(value):
        int_value = int(value * factor)
        slider.setValue(int_value)
        if value_lbl:
            value_lbl.setText(f"{value:.{decimals}f}")
    
    slider.valueChanged.connect(slider_changed)
    spinbox.valueChanged.connect(spinbox_changed)
    
    if parent_layout:
        parent_layout.addLayout(layout)
        
    return slider, spinbox, value_lbl

def bind_controls(controls: List[Union[QSlider, QSpinBox, QDoubleSpinBox]],
                  value_labels: Optional[List[QLabel]] = None,
                  factor: Optional[List[float]] = None):
    """Bind multiple controls to update together."""
    if not controls:
        return
        
    if factor is None:
        factor = [1.0] * len(controls)
        
    def update_all(source, value):
        for i, control in enumerate(controls):
            if control != source:
                if isinstance(control, QSlider):
                    control.setValue(int(value * factor[i]))
                elif isinstance(control, (QSpinBox, QDoubleSpinBox)):
                    control.setValue(value * factor[i])
                    
        if value_labels:
            for i, label in enumerate(value_labels):
                if label:
                    label.setText(f"{value * factor[i]:.2f}")
                    
    for control in controls:
        if isinstance(control, QSlider):
            control.valueChanged.connect(lambda value, c=control: update_all(c, value))
        elif isinstance(control, (QSpinBox, QDoubleSpinBox)):
            control.valueChanged.connect(lambda value, c=control: update_all(c, value))