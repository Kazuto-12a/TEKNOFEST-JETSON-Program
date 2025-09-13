from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox,
    QFrame, QLineEdit, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator
from slide_switch import SlideSwitch


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

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main card
        card = QFrame()
        card.setObjectName("auto-control-panel")
        card.setFrameShape(QFrame.StyledPanel)
        card.setFrameShadow(QFrame.Raised)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(18)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card.setStyleSheet("""
            QFrame#auto-control-panel {
                background-color: #2d383c;
                border-radius: 12px;
                border: 1px solid #414c50;
            }
        """)

        # Mode row
        mode_row = QHBoxLayout()
        mode_label = QLabel("Mode Kontrol:")
        mode_label.setFont(QFont("", 10, QFont.Bold))
        mode_switch = AutoModeSwitch()
        mode_row.addWidget(mode_label)
        mode_row.addStretch()
        mode_row.addWidget(mode_switch)
        card_layout.addLayout(mode_row)

        # Plant profile row
        plant_row = QHBoxLayout()
        plant_label = QLabel("Plant Profile:")
        plant_label.setFont(QFont("", 10, QFont.Bold))
        plant_dropdown = CustomComboBox()
        plant_dropdown.addItems(["Lettuce", "Tomato", "Spinach", "Kale", "Strawberry"])
        plant_row.addWidget(plant_label)
        plant_row.addStretch()
        plant_row.addWidget(plant_dropdown)
        card_layout.addLayout(plant_row)

        # Acclimation row
        accl_row = QHBoxLayout()
        accl_label = QLabel("Acclamation Duration (Days):")
        accl_label.setFont(QFont("", 10, QFont.Bold))
        self.accl_input = CustomLineEdit()
        accl_row.addWidget(accl_label)
        accl_row.addStretch()
        accl_row.addWidget(self.accl_input)
        card_layout.addLayout(accl_row)

        # Spacer + button
        card_layout.addItem(QSpacerItem(10, 8, QSizePolicy.Minimum, QSizePolicy.Expanding))
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
        card_layout.addWidget(start_btn, alignment=Qt.AlignCenter)

        main_layout.addWidget(card, alignment=Qt.AlignHCenter)
        main_layout.addStretch()
