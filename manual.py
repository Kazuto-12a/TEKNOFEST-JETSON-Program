import random
import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGridLayout, QSlider, QPushButton
)
from PySide6.QtCore import Qt, Slot
from settings import Settings
from slide_switch import SlideSwitch

class Manual(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("manual-container")
        self.control_widgets = []
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)
        # Device toggles
        device_buttons_container = QWidget()
        device_buttons_container.setObjectName("device-buttons-container")
        layout = QHBoxLayout(device_buttons_container)
        layout.setSpacing(18)
        layout.setContentsMargins(10, 10, 10, 10)
        def create_toggle(label_text, cmd):
            vbox = QVBoxLayout()
            vbox.setAlignment(Qt.AlignCenter)
            label = QLabel(label_text)
            label.setObjectName("toggle-label")
            switch = SlideSwitch()
            switch.setChecked(False)
            switch.toggled.connect(lambda checked, c=cmd: Settings.send_command(f"{c}{'1' if checked else '0'}\n"))
            vbox.addWidget(label)
            vbox.addWidget(switch)
            widget = QWidget()
            widget.setLayout(vbox)
            self.control_widgets.append(switch)
            return widget
        layout.addWidget(create_toggle("UV Light", "U"))
        layout.addWidget(create_toggle("Indicator Light", "L"))
        layout.addWidget(create_toggle("Humidifier", "H"))
        layout.addWidget(create_toggle("Water Pump", "W"))
        main_layout.addWidget(device_buttons_container)
        # Sliders
        sliders_container = QWidget()
        sliders_container.setObjectName("sliders-container")
        grid = QGridLayout(sliders_container)
        grid.setSpacing(16)
        grid.setContentsMargins(10, 10, 10, 10)
        def create_slider(label_text, cmd, row, col):
            vbox = QVBoxLayout()
            label = QLabel(label_text)
            label.setObjectName("slider-label")
            slider = QSlider(Qt.Horizontal)
            slider.setObjectName("device-slider")
            slider.setRange(0, 255)
            value_label = QLabel(f"{slider.value()}")
            value_label.setObjectName("slider-value-label")
            slider.valueChanged.connect(value_label.setNum)
            slider.sliderReleased.connect(lambda c=cmd, s=slider: Settings.send_command(f"{c}{s.value()}\n"))
            hbox = QHBoxLayout()
            hbox.addWidget(slider)
            hbox.addWidget(value_label)
            vbox.addWidget(label)
            vbox.addLayout(hbox)
            widget = QWidget()
            widget.setLayout(vbox)
            grid.addWidget(widget, row, col)
            self.control_widgets.append(slider)
        create_slider("Kipas Peltier", "P", 0, 0)
        create_slider("Kipas Radiator", "R", 0, 1)
        create_slider("Peltier PWM", "D", 1, 0)
        create_slider("Grow Light (Merah)", "G", 1, 1)
        create_slider("Grow Light (Biru)", "B", 2, 0)
        main_layout.addWidget(sliders_container)
        main_layout.addStretch()
    @Slot(bool)
    def set_controls_enabled(self, enabled):
        for widget in self.control_widgets:
            widget.setEnabled(enabled)
