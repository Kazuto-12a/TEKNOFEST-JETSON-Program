from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QRectF, QPropertyAnimation, Property, QEasingCurve
from PySide6.QtGui import QPainter, QPen, QColor, QLinearGradient, QBrush, QFont


class HalfCircleGauge(QWidget):
    def __init__(self, parent=None, min_temp=20, max_temp=40):
        super().__init__(parent)
        self._value = 0.0  # Nilai gauge (0-100)
        self._target_value = 0.0
        self.temperature = 25.0  # Nilai suhu aktual
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.setMinimumSize(220, 130)
        # Animasi perubahan nilai
        self.anim = QPropertyAnimation(self, b"value", self)
        self.anim.setDuration(600)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        # Warna sesuai tema UI
        self.bg_color = QColor("#2d383c")
        self.arc_bg_color = QColor("#414c50")
        self.arc_fg_color = QColor("#39ace7")
        self.text_color = QColor("#b3e5fc")
        self.temp_text_color = QColor("#ffd600")

    def setValue(self, value):
        value = max(0, min(100, value))
        self._target_value = value
        # Animasi perubahan nilai
        if hasattr(self, "anim") and self.anim is not None:
            try:
                self.anim.stop()
            except RuntimeError:
                return
            self.anim.setStartValue(self._value)
            self.anim.setEndValue(value)
            self.anim.start()

    def getValue(self):
        return self._value

    value = Property(float, fget=getValue, fset=lambda self, v: setattr(self, "_value", v) or self.update())

    def setTemperature(self, temp):
        """Set suhu aktual dan update gauge."""
        temp = max(self.min_temp, min(self.max_temp, temp))
        self.temperature = temp
        mapped = int((temp - self.min_temp) * 100 / (self.max_temp - self.min_temp))
        self.setValue(mapped)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        # Add top margin to move arc lower and avoid overlap with label
        top_margin = 32
        size = min(width, (height - top_margin) * 2)
        radius = int(size / 2 - 10)
        center_x = rect.center().x()
        center_y = rect.bottom() - 10
        arc_rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Draw background
        painter.setBrush(self.bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(rect)

        # Draw label above the arc
        if hasattr(self, 'label_text') and self.label_text:
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(self.text_color)
            label_rect = QRectF(
                arc_rect.left(),
                arc_rect.top() - 32,  # Move label higher above the arc
                arc_rect.width(),
                28
            )
            painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignVCenter, self.label_text)

        # Background arc (dark blue/gray)
        pen_bg = QPen(self.arc_bg_color, 18)
        painter.setPen(pen_bg)
        painter.drawArc(arc_rect, 180 * 16, -180 * 16)

        # Foreground arc (bright blue)
        pen_fg = QPen(self.arc_fg_color, 18)
        pen_fg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_fg)
        span_angle = int(-180 * 16 * (self._value / 100))
        painter.drawArc(arc_rect, 180 * 16, span_angle)

        # Temperature text in the center
        temp_text = f"{self.temperature:.1f} °C"
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(self.temp_text_color)
        temp_rect = QRectF(
            arc_rect.left(),
            arc_rect.top() + arc_rect.height() / 8,
            arc_rect.width(),
            arc_rect.height() / 2
        )
        painter.drawText(temp_rect, Qt.AlignHCenter | Qt.AlignVCenter, temp_text)


class StripGauge(QWidget):
    def __init__(self, parent=None, value=0, min_value=0, max_value=100):
        super().__init__(parent)
        self._value = value
        self._min = min_value
        self._max = max_value
        self.setMinimumHeight(22)
        self.setMaximumHeight(26)
        self.setMinimumWidth(120)
        # Animasi perubahan nilai
        self.anim = QPropertyAnimation(self, b"value", self)
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        # Warna sesuai tema UI
        self.bg_color = QColor("#414c50")
        self.fg_color = QColor("#39ace7")
        self.border_color = QColor("#b3e5fc")

    def setRange(self, min_value, max_value):
        self._min = min_value
        self._max = max_value
        self.update()

    def setValue(self, value):
        value = max(self._min, min(self._max, value))
        if hasattr(self, "anim") and self.anim is not None:
            try:
                self.anim.stop()
            except RuntimeError:
                return
            self.anim.setStartValue(self._value)
            self.anim.setEndValue(value)
            self.anim.start()
        else:
            self._value = value
            self.update()

    def getValue(self):
        return self._value

    value = Property(int, fget=getValue, fset=lambda self, v: setattr(self, "_value", v) or self.update())

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        # Background strip (dark blue)
        painter.setPen(QPen(self.border_color, 1.5))
        painter.setBrush(self.bg_color)
        painter.drawRoundedRect(rect, 8, 8)
        # Filled part (bright blue)
        fill_width = rect.width() * self._value / 100
        grad = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
        grad.setColorAt(0, self.fg_color)
        grad.setColorAt(1, QColor("#81c784"))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        fill_rect = QRectF(rect.left(), rect.top(), fill_width, rect.height())
        painter.drawRoundedRect(fill_rect, 8, 8)


class SensorGaugesWidget(QWidget):
    def __init__(self, sensor_values, parent=None):
        super().__init__(parent)
        self.sensor_values = sensor_values

        layout = QHBoxLayout()
        layout.setSpacing(24)
        self.setLayout(layout)

        # Gauge suhu (half circle)
        self.gauge = HalfCircleGauge()
        temp_gauge_container = QVBoxLayout()
        self.temp_label = QLabel("🌡️ Temperature")
        self.temp_label.setObjectName("tempLabel")
        self.temp_label.setAlignment(Qt.AlignCenter)
        self.temp_label.setProperty("sensor-label", True)
        temp_gauge_container.addWidget(self.temp_label)
        temp_gauge_container.addWidget(self.gauge)
        temp_gauge_widget = QWidget()
        temp_gauge_widget.setLayout(temp_gauge_container)
        layout.addWidget(temp_gauge_widget)

        # Gauge CO2
        co2_container = QVBoxLayout()
        co2_label = QLabel("🟢 CO₂ (ppm)")
        co2_label.setAlignment(Qt.AlignCenter)
        co2_label.setProperty("sensor-label", True)
        self.co2_gauge = StripGauge(value=self.sensor_values["co2"] // 20)
        self.co2_value_label = QLabel(f"{self.sensor_values['co2']} ppm")
        self.co2_value_label.setAlignment(Qt.AlignCenter)
        self.co2_value_label.setProperty("sensor-value", True)
        co2_container.addWidget(co2_label)
        co2_container.addWidget(self.co2_gauge)
        co2_container.addWidget(self.co2_value_label)
        co2_widget = QWidget()
        co2_widget.setLayout(co2_container)
        layout.addWidget(co2_widget)

        # Gauge TVOC
        tvoc_container = QVBoxLayout()
        tvoc_label = QLabel("🧪 TVOC (mg/m³)")
        tvoc_label.setAlignment(Qt.AlignCenter)
        tvoc_label.setProperty("sensor-label", True)
        self.tvoc_gauge = StripGauge(value=int(self.sensor_values["tvoc"] * 50))
        self.tvoc_value_label = QLabel(f"{self.sensor_values['tvoc']} mg/m³")
        self.tvoc_value_label.setAlignment(Qt.AlignCenter)
        self.tvoc_value_label.setProperty("sensor-value", True)
        tvoc_container.addWidget(tvoc_label)
        tvoc_container.addWidget(self.tvoc_gauge)
        tvoc_container.addWidget(self.tvoc_value_label)
        tvoc_widget = QWidget()
        tvoc_widget.setLayout(tvoc_container)
        layout.addWidget(tvoc_widget)

        # Gauge Humidity
        hum_container = QVBoxLayout()
        hum_label = QLabel("💧 Humidity (%)")
        hum_label.setAlignment(Qt.AlignCenter)
        hum_label.setProperty("sensor-label", True)
        self.hum_gauge = StripGauge(value=self.sensor_values["hum"])
        self.hum_value_label = QLabel(f"{self.sensor_values['hum']}%")
        self.hum_value_label.setAlignment(Qt.AlignCenter)
        self.hum_value_label.setProperty("sensor-value", True)
        hum_container.addWidget(hum_label)
        hum_container.addWidget(self.hum_gauge)
        hum_container.addWidget(self.hum_value_label)
        hum_widget = QWidget()
        hum_widget.setLayout(hum_container)
        layout.addWidget(hum_widget)

        # Gauge Lux
        lux_container = QVBoxLayout()
        lux_label = QLabel("💡 Lux")
        lux_label.setAlignment(Qt.AlignCenter)
        lux_label.setProperty("sensor-label", True)
        self.lux_gauge = StripGauge(value=min(self.sensor_values["lux"] // 20, 100))
        self.lux_value_label = QLabel(f"{self.sensor_values['lux']} lux")
        self.lux_value_label.setAlignment(Qt.AlignCenter)
        self.lux_value_label.setProperty("sensor-value", True)
        lux_container.addWidget(lux_label)
        lux_container.addWidget(self.lux_gauge)
        lux_container.addWidget(self.lux_value_label)
        lux_widget = QWidget()
        lux_widget.setLayout(lux_container)
        layout.addWidget(lux_widget)

    def update_sensors(self, sensor_values):
        """Update semua gauge dan label dengan nilai sensor baru."""
        self.sensor_values = sensor_values
        self.gauge.setTemperature(self.sensor_values["temp"])
        self.co2_gauge.setValue(self.sensor_values["co2"] // 20)
        self.co2_value_label.setText(f"{self.sensor_values['co2']} ppm")
        self.tvoc_gauge.setValue(int(self.sensor_values["tvoc"] * 50))
        self.tvoc_value_label.setText(f"{self.sensor_values['tvoc']} mg/m³")
        self.hum_gauge.setValue(self.sensor_values["hum"])
        self.hum_value_label.setText(f"{self.sensor_values['hum']}%")
        self.lux_gauge.setValue(min(self.sensor_values["lux"] // 20, 100))
        self.lux_value_label.setText(f"{self.sensor_values['lux']} lux")