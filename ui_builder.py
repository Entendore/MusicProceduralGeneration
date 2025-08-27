# ui_builder.py
from PyQt6.QtWidgets import (
    QLabel, QSlider, QSpinBox, QDoubleSpinBox, QPushButton, QWidget,
    QCheckBox, QComboBox, QLayout, QFrame, QGroupBox, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from typing import Optional, Tuple, List, Union
from themes import DARK_THEME, LIGHT_THEME

class UIBuilder:
    def __init__(self, parent_layout: QLayout):
        self.layout = parent_layout

    # ---------- Theme & Style ----------
    def apply_theme(self, widget: Optional[QWidget] = None, theme: str = "dark"):
        """
        Apply a theme to a widget or the whole application.
        :param widget: The QWidget to style. If None, applies to QApplication instance.
        :param theme: 'dark' or 'light'
        """
        style = DARK_THEME if theme.lower() == "dark" else LIGHT_THEME
        if widget is None:
            # Apply to QApplication instance
            from PyQt6.QtWidgets import QApplication
            QApplication.instance().setStyleSheet(style)
        else:
            widget.setStyleSheet(style)

    def set_font_size(self, widget: QWidget, size: int):
        """Set font size of a widget."""
        font = widget.font()
        font.setPointSize(size)
        widget.setFont(font)

    def set_font_bold(self, widget: QWidget, bold: bool = True):
        """Set font boldness of a widget."""
        font = widget.font()
        font.setBold(bold)
        widget.setFont(font)

    # ---------- Basic controls ----------
    def add_slider(self, label: str, min_val: int, max_val: int, default: int,
                   orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                   tooltip: Optional[str] = None,
                   link_value_label: Optional[QLabel] = None) -> QSlider:
        from ui_controls import make_slider
        return make_slider(label, min_val, max_val, default, orientation, self.layout,
                           tooltip, link_value_label=link_value_label)

    def add_spinbox(self, label: str, min_val: int, max_val: int, default: int,
                    tooltip: Optional[str] = None, step: int = 1,
                    link_value_label: Optional[QLabel] = None) -> QSpinBox:
        from ui_controls import make_spinbox
        return make_spinbox(label, min_val, max_val, default, self.layout,
                            tooltip, step, link_value_label=link_value_label)

    def add_button(self, label: str, tooltip: Optional[str] = None,
                   checkable: bool = False) -> QPushButton:
        from ui_controls import make_button
        return make_button(label, self.layout, tooltip, checkable)

    def add_checkbox(self, label: str, default: bool = False,
                     tooltip: Optional[str] = None) -> QCheckBox:
        from ui_controls import make_checkbox
        return make_checkbox(label, default, self.layout, tooltip)

    def add_combo(self, label: str, items: List[str], default: str,
                  tooltip: Optional[str] = None) -> QComboBox:
        from ui_controls import make_combo
        return make_combo(label, items, default, self.layout, tooltip)

    def add_label_value(self, label: str, default: str = "",
                        tooltip: Optional[str] = None,
                        orientation: str = "horizontal") -> Tuple[QLabel, QLabel]:
        from ui_controls import make_label_value
        return make_label_value(label, default, self.layout, tooltip, orientation)

    # ---------- Containers ----------
    def add_groupbox(self, title: str, orientation: str = "vertical") -> Tuple[QGroupBox, QLayout]:
        from ui_controls import make_groupbox
        return make_groupbox(title, self.layout, orientation)

    def add_frame(self, orientation: str = "vertical",
                  frame_shape: QFrame.Shape = QFrame.Shape.StyledPanel,
                  frame_shadow: QFrame.Shadow = QFrame.Shadow.Raised) -> Tuple[QFrame, QLayout]:
        from ui_controls import make_frame
        return make_frame(self.layout, orientation, frame_shape, frame_shadow)

    # ---------- Synced controls ----------
    def add_synced_slider(self, label: str, min_val: int, max_val: int, default: int,
                          show_value_label: bool = True, step: int = 1,
                          tooltip: Optional[str] = None) -> Tuple[QSlider, QSpinBox, Optional[QLabel]]:
        from ui_controls import make_synced_slider
        return make_synced_slider(label, min_val, max_val, default,
                                  self.layout, tooltip, show_value_label=show_value_label, step=step)

    def add_synced_slider_float(self, label: str, min_val: float, max_val: float, default: float,
                                decimals: int = 2, step: float = 0.1,
                                show_value_label: bool = True, tooltip: Optional[str] = None
                                ) -> Tuple[QSlider, QDoubleSpinBox, Optional[QLabel]]:
        from ui_controls import make_synced_slider_float
        return make_synced_slider_float(label, min_val, max_val, default,
                                        self.layout, tooltip, decimals, show_value_label, step)

    # ---------- Binding ----------
    def bind_controls(self, controls: List[Union[QSlider, QSpinBox, QDoubleSpinBox]],
                      value_labels: Optional[List[QLabel]] = None,
                      factor: Optional[List[float]] = None):
        from ui_controls import bind_controls
        bind_controls(controls, value_labels, factor)

    # ---------- Layout Helpers ----------
    def add_spacing(self, size: int = 10):
        """Add vertical spacing in the layout."""
        from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
        spacer = QSpacerItem(20, size, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addItem(spacer)

    def add_separator(self, horizontal: bool = True):
        """Add a line separator."""
        from PyQt6.QtWidgets import QFrame
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine if horizontal else QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)

    def add_title_label(self, text: str, bold: bool = True):
        """Add a section title label."""
        lbl = QLabel(text)
        font = lbl.font()
        font.setBold(bold)
        font.setPointSize(font.pointSize() + 2)
        lbl.setFont(font)
        self.layout.addWidget(lbl)
        return lbl

    # ---------- Nested Builder ----------
    def nested_builder(self, layout: QLayout) -> 'UIBuilder':
        """Return a UIBuilder for a nested layout."""
        return UIBuilder(layout)