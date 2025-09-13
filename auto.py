from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox,
    QFrame, QLineEdit, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator
from slide_switch import SlideSwitch
import json
import os


# -------------------------
# Custom small controls
# -------------------------
class AutoModeSwitch(SlideSwitch):
    """Extended SlideSwitch with text labels for Auto mode, styled to match the UI palette."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(170)
        self.setMaximumWidth(200)
        self.setMinimumHeight(44)
        self.setFont(QFont("", 11, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("")  # Remove parent stylesheet, use custom paint
        self.update()
        self.toggled.connect(self.update)

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QColor, QFont
        from PySide6.QtCore import QRectF
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        # Background color
        if self.isChecked():
            bg_color = QColor("#39ace7")  # biru terang
            text_color = QColor("#192428")
        else:
            bg_color = QColor("#414c50")  # abu gelap
            text_color = QColor("#ffffff")
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(r, r.height()/2, r.height()/2)
        # Draw knob
        knob_margin = 4
        knob_diameter = r.height() - 2*knob_margin
        y = r.y() + knob_margin
        if self.isChecked():
            x = r.right() - knob_diameter - knob_margin
        else:
            x = r.x() + knob_margin
        painter.setBrush(QColor("#fff"))
        painter.drawEllipse(x, y, knob_diameter, knob_diameter)
        # Draw text
        painter.setFont(self.font())
        painter.setPen(text_color)
        text = "Automated" if self.isChecked() else "Manual"
        painter.drawText(QRectF(r), Qt.AlignCenter, text)


class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("auto-plant-dropdown")
        self.setFixedHeight(36)
        self.setMinimumWidth(160)
        self.setFont(QFont("", 10, QFont.Bold))
        self.setStyleSheet("""
            QComboBox#auto-plant-dropdown {
                background-color: #192428;
                color: #ffffff;
                border: 1px solid #414c50;
                border-radius: 8px;
                padding: 6px 10px;
            }
            QComboBox#auto-plant-dropdown:hover {
                border: 1px solid #39ace7;
            }
            QComboBox#auto-plant-dropdown::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border-left-width: 0px;
            }
            QComboBox#auto-plant-dropdown QAbstractItemView {
                background-color: #2d383c;
                color: #ffffff;
                border: 1px solid #414c50;
                padding: 6px;
                outline: none;
            }
            QComboBox#auto-plant-dropdown QAbstractItemView::item:selected {
                background: #39ace7;
                color: #192428;
            }
        """)


class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("auto-days-input")
        self.setFixedWidth(90)
        self.setFixedHeight(36)
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setPlaceholderText("0")
        self.setFont(QFont("", 10, QFont.Bold))
        self.setValidator(QIntValidator(0, 999))  # only numbers allowed
        self.setStyleSheet("""
            QLineEdit#auto-days-input {
                background-color: #192428;
                color: #ffffff;
                border: 1px solid #414c50;
                border-radius: 8px;
                padding: 6px 8px;
            }
            QLineEdit#auto-days-input:focus {
                border: 1px solid #39ace7;
            }
        """)


# -------------------------
# Main Auto panel
# -------------------------
class Auto(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("menu-box")
        self.setStyleSheet("""
            QWidget#menu-box {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #22303a, stop:1 #192428);
            }
            QFrame#auto-controls-card:hover, QFrame#profile-info-box:hover {
                border: 2.5px solid #81c784;
            }
        """)
        # --- Main horizontal layout for centering ---
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        # --- Title with icon ---
        title_row = QHBoxLayout()
        title_icon = QLabel("\U0001F916")  # 🤖
        title_icon.setStyleSheet("font-size:28px;margin-right:8px;")
        title_label = QLabel("Auto Control Mode")
        title_label.setFont(QFont("", 18, QFont.Bold))
        title_label.setStyleSheet("color:#39ace7;")
        title_row.addWidget(title_icon, 0, Qt.AlignTop | Qt.AlignVCenter)
        title_row.addWidget(title_label, 0, Qt.AlignTop | Qt.AlignVCenter)
        title_row.addStretch()
        outer_layout.addLayout(title_row)
        outer_layout.addSpacing(12)
        # --- Row container for cards ---
        row_container = QWidget()
        row_layout = QHBoxLayout(row_container)
        row_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(32)
        # --- LEFT CARD: Controls ---
        controls_card = QFrame()
        controls_card.setObjectName("auto-controls-card")
        controls_card.setFrameShape(QFrame.StyledPanel)
        controls_card.setFrameShadow(QFrame.Raised)
        controls_card.setStyleSheet("""
            QFrame#auto-controls-card {
                background-color: #2d383c;
                border-radius: 16px;
                border: 1.5px solid #39ace7;
                min-width: 320px;
                max-width: 360px;
                padding: 32px 36px;
            }
        """)
        controls_col = QVBoxLayout(controls_card)
        controls_col.setSpacing(18)
        controls_col.setAlignment(Qt.AlignTop)
        # Mode row
        mode_label = QLabel("Mode Kontrol:")
        mode_label.setFont(QFont("", 10, QFont.Bold))
        mode_switch = AutoModeSwitch()
        controls_col.addWidget(mode_label)
        controls_col.addWidget(mode_switch)
        # Plant profile row
        plant_label = QLabel("Plant Profile:")
        plant_label.setFont(QFont("", 10, QFont.Bold))
        self.plant_dropdown = CustomComboBox()
        self.plant_dropdown.addItems(["Lettuce", "Tomato", "Spinach", "Kale", "Strawberry"])
        controls_col.addWidget(plant_label)
        controls_col.addWidget(self.plant_dropdown)
        # Acclimation row
        accl_label = QLabel("Acclamation Duration (Days):")
        accl_label.setFont(QFont("", 10, QFont.Bold))
        self.accl_input = CustomLineEdit()
        controls_col.addWidget(accl_label)
        controls_col.addWidget(self.accl_input)
        # Spacer + button
        controls_col.addStretch()
        start_btn = QPushButton("Start Process")
        start_btn.setObjectName("auto-start-btn")
        start_btn.setFixedHeight(44)
        start_btn.setFont(QFont("", 10, QFont.Bold))
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.setStyleSheet("""
            QPushButton#auto-start-btn {
                background-color: #39ace7;
                color: #192428;
                border-radius: 10px;
                padding: 8px 18px;
            }
            QPushButton#auto-start-btn:hover {
                background-color: #57c7f6;
            }
        """)
        controls_col.addWidget(start_btn)
        self.start_btn = start_btn  # Save reference for slot
        start_btn.clicked.connect(self.handle_start_process)
        # --- RIGHT CARD: Profile Info ---
        self.profile_info_box = QFrame()
        self.profile_info_box.setObjectName("profile-info-box")
        self.profile_info_box.setFrameShape(QFrame.StyledPanel)
        self.profile_info_box.setFrameShadow(QFrame.Raised)
        self.profile_info_box.setStyleSheet("""
            QFrame#profile-info-box {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #26343c, stop:1 #22303a);
                border-radius: 18px;
                border: 2.5px solid #39ace7;
                padding: 36px 38px 32px 38px;
                min-width: 320px;
                max-width: 370px;
            }
        """)
        self.profile_info_layout = QVBoxLayout(self.profile_info_box)
        self.profile_info_layout.setAlignment(Qt.AlignTop)
        # --- Inner header box ---
        self.header_box = QFrame()
        self.header_box.setObjectName("profile-header-box")
        self.header_box.setStyleSheet("""
            QFrame#profile-header-box {
                background: rgba(57,172,231,0.08);
                border-radius: 14px;
                padding: 18px 10px 12px 10px;
                margin-bottom: 18px;
                border: 1.5px solid #39ace7;
            }
            QFrame#profile-header-box:hover {
                background: rgba(129,199,132,0.13);
                border: 1.5px solid #81c784;
            }
        """)
        header_vbox = QVBoxLayout(self.header_box)
        header_vbox.setAlignment(Qt.AlignHCenter)
        header_vbox.setSpacing(4)
        self.profile_header = QLabel()
        self.profile_header.setFont(QFont("", 22, QFont.Bold))
        self.profile_header.setStyleSheet("color:#b3e5fc;font-size:24px;margin-bottom:2px;")
        self.profile_header.setText("")
        header_vbox.addWidget(self.profile_header, alignment=Qt.AlignHCenter)
        self.profile_illustration = QLabel("")
        self.profile_illustration.setAlignment(Qt.AlignHCenter)
        self.profile_illustration.setStyleSheet("font-size:54px;margin-bottom:2px;")
        header_vbox.addWidget(self.profile_illustration)
        self.profile_subtitle = QLabel("Optimal Growth Conditions")
        self.profile_subtitle.setAlignment(Qt.AlignHCenter)
        self.profile_subtitle.setStyleSheet("color:#b3e5fc;font-size:15px;margin-bottom:0px;")
        header_vbox.addWidget(self.profile_subtitle)
        self.profile_info_layout.addWidget(self.header_box)
        # --- Parameter card ---
        self.param_card = QFrame()
        self.param_card.setObjectName("profile-param-card")
        self.param_card.setStyleSheet("""
            QFrame#profile-param-card {
                background: rgba(41, 60, 70, 0.85);
                border-radius: 12px;
                padding: 18px 12px 12px 18px;
                margin-top: 8px;
                margin-bottom: 0px;
                border: 1px solid #414c50;
            }
        """)
        param_vbox = QVBoxLayout(self.param_card)
        param_vbox.setAlignment(Qt.AlignTop)
        param_vbox.setSpacing(8)
        self.profile_labels = {}
        param_info = [
            ("temp", "Temp", "°C", "<span style='color:#e57373;'>\U0001F321</span>", "Target temperature for this plant."),
            ("hum", "Humidity", "%", "<span style='color:#00bcd4;'>\U0001F4A7</span>", "Target humidity for this plant."),
            ("lux", "Lux", "lx", "<span style='color:#ffd600;'>\U0001F4A1</span>", "Target light intensity (lux) for this plant."),
            ("co2", "CO₂", "ppm", "<span style='color:#81c784;'>\U0001F7E2</span>", "Target CO₂ concentration for this plant.")
        ]
        for key, label, unit, icon, tip in param_info:
            l = QLabel()
            l.setObjectName(f"profile-{key}-label")
            l.setStyleSheet("color:#b3e5fc;font-size:17px;font-weight:bold;margin-bottom:8px;")
            l.setToolTip(tip)
            l.setText(f"{icon} <b>{label}:</b> - {unit}")
            l.setTextFormat(Qt.RichText)
            param_vbox.addWidget(l)
            self.profile_labels[key] = l
        self.profile_info_layout.addWidget(self.param_card)
        # Add both cards to row layout
        row_layout.addWidget(controls_card, 0)
        row_layout.addWidget(self.profile_info_box, 0)
        # Add row container to outer layout
        outer_layout.addWidget(row_container, alignment=Qt.AlignHCenter | Qt.AlignTop)
        outer_layout.addStretch()
        # Load plant profiles and connect dropdown
        self._load_plant_profiles()
        self.plant_dropdown.clear()
        self.plant_dropdown.addItems(list(self.plant_profiles.keys()))
        self.plant_dropdown.currentTextChanged.connect(self._update_profile_info)
        self._update_profile_info(self.plant_dropdown.currentText())

    def _load_plant_profiles(self):
        self.plant_profiles = {}
        json_path = os.path.join(os.path.dirname(__file__), "plant_profiles.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    self.plant_profiles = json.load(f)
            except Exception as e:
                print(f"Error loading plant profiles: {e}")
        if not self.plant_profiles:
            # Default profiles if file not found or empty
            self.plant_profiles = {
                "Lettuce": {"temp": 22, "hum": 60, "lux": 12000, "co2": 800},
                "Tomato": {"temp": 25, "hum": 65, "lux": 15000, "co2": 1000},
                "Spinach": {"temp": 20, "hum": 70, "lux": 10000, "co2": 900},
                "Kale": {"temp": 18, "hum": 75, "lux": 9000, "co2": 850},
                "Strawberry": {"temp": 21, "hum": 60, "lux": 14000, "co2": 950},
                "Basil": {"temp": 24, "hum": 55, "lux": 13000, "co2": 850},
                "Cucumber": {"temp": 26, "hum": 70, "lux": 16000, "co2": 1100}
            }

    def _update_profile_info(self, plant_name):
        profile = self.plant_profiles.get(plant_name, {})
        # Update header
        plant_icon = "<span style='font-size:22px;'>\U0001F331</span>"  # 🌱
        self.profile_header.setText(f"{plant_icon} <span style='color:#b3e5fc;'>{plant_name}</span>")
        # Update illustration based on plant
        plant_emoji = {
            "Lettuce": "\U0001F957",      # 🥗
            "Tomato": "\U0001F345",      # 🍅
            "Spinach": "\U0001F96C",     # 🥬
            "Kale": "\U0001F96C",        # 🥬
            "Strawberry": "\U0001F353",  # 🍓
            "Basil": "\U0001FAD2",       # 🫒 (closest emoji)
            "Cucumber": "\U0001F952"      # 🥒
        }.get(plant_name, "\U0001F331")
        self.profile_illustration.setText(plant_emoji)
        # Update parameters
        param_info = {
            "temp": ("<span style='color:#e57373;'>\U0001F321</span>", "Temp", "°C"),
            "hum": ("<span style='color:#00bcd4;'>\U0001F4A7</span>", "Humidity", "%"),
            "lux": ("<span style='color:#ffd600;'>\U0001F4A1</span>", "Lux", "lx"),
            "co2": ("<span style='color:#81c784;'>\U0001F7E2</span>", "CO₂", "ppm")
        }
        for key, label in self.profile_labels.items():
            val = profile.get(key, '-')
            icon, lbl, unit = param_info[key]
            label.setText(f"{icon} <b>{lbl}:</b> {val} {unit}")
            label.setTextFormat(Qt.RichText)

    def handle_start_process(self):
        self.start_btn.setEnabled(False)
        self.start_btn.setText("Processing...")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(5000, self.reset_start_button)

    def reset_start_button(self):
        self.start_btn.setEnabled(True)
        self.start_btn.setText("Start Process")
