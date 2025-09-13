from PySide6.QtWidgets import QPushButton, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen


class SlideSwitch(QPushButton):
    """True oval slider style ON/OFF switch, themed for dark blue palette."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(38)
        self.setMinimumWidth(68)
        self.setMaximumWidth(68)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setObjectName("slide-switch")
        self.setStyleSheet("border: none;")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        # Colors from your palette
        on_color = QColor("#39ace7")
        off_color = QColor("#414c50")
        knob_shadow = QColor(0,0,0,40)
        # Draw background
        bg_color = on_color if self.isChecked() else off_color
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(r, r.height()/2, r.height()/2)
        # Draw knob
        knob_margin = 5
        knob_diameter = r.height() - 2*knob_margin
        y = r.y() + knob_margin
        if self.isChecked():
            x = r.right() - knob_diameter - knob_margin
        else:
            x = r.x() + knob_margin
        # Shadow
        painter.setBrush(knob_shadow)
        painter.drawEllipse(x, y+2, knob_diameter, knob_diameter)
        # Knob
        painter.setBrush(QColor("#fff"))
        painter.setPen(QPen(QColor("#b0bec5"), 1))
        painter.drawEllipse(x, y, knob_diameter, knob_diameter)
