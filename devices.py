import json
import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGridLayout, QSlider, QPushButton
)
from PySide6.QtCore import Qt, Slot, QTimer
from gauges import HalfCircleGauge, StripGauge
from settings import Settings
from slide_switch import SlideSwitch


DEBUG_GAUGE = False  # Set True to test gauge with random data


class Devices(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("devices-container")
        self.control_widgets = []

        # Layout utama: kiri (konten), kanan (sidebar gauges)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # Konten utama (box putih)
        self.main_content = QWidget()
        self.main_content.setObjectName("menu-box")
        self.main_content_layout = QVBoxLayout(self.main_content)
        self.main_content_layout.setAlignment(Qt.AlignTop)
        self.main_content_layout.setSpacing(18)

        # Hapus AC control, hanya device toggles dan sliders
        self._setup_device_toggles()
        self._setup_sliders()

        # Sidebar gauges
        self._setup_sidebar_gauges()

        # Tambahkan ke layout utama
        main_layout.addWidget(self.main_content, 2)
        main_layout.addWidget(self.sidebar_gauges_container, 1)

        # Timer polling data sensor
        self.serial_read_timer = QTimer(self)
        self.serial_read_timer.timeout.connect(self.request_and_update_sensors)
        self.serial_read_timer.start(2000)
        # Debug gauge timer
        if DEBUG_GAUGE:
            self.debug_timer = QTimer(self)
            self.debug_timer.timeout.connect(self._debug_update_gauges)
            self.debug_timer.start(2000)

        # Awal: semua kontrol nonaktif
        self.set_controls_enabled(True)

    def request_and_update_sensors(self):
        """Kirim perintah baca sensor ke serial jika terkoneksi."""
        if Settings.is_connected():
            Settings.send_command('S\n')
            QTimer.singleShot(100, self.read_and_process_data)

    def read_and_process_data(self):
        """Baca data sensor dari serial dan update gauge jika format JSON."""
        line = Settings.read_data()
        if line:
            try:
                if line.strip().startswith("{") and line.strip().endswith("}"):
                    sensor_data = json.loads(line)
                    self.update_gauges_from_dict(sensor_data)
            except json.JSONDecodeError:
                pass

    @Slot(bool)
    def set_controls_enabled(self, enabled):
        """Aktifkan/nonaktifkan semua kontrol perangkat."""
        print(f"[DEVICES] Mengatur semua kontrol ke status: {'Aktif' if enabled else 'Nonaktif'}")
        for widget in self.control_widgets:
            widget.setEnabled(enabled)

    def update_gauges_from_dict(self, sensor_data):
        """Update nilai gauge sidebar dari dict sensor_data. Fungsi ini bisa dipanggil dari luar."""
        if hasattr(self, 'sidebar_temp_gauge'):
            self.sidebar_temp_gauge.setTemperature(sensor_data.get("temp", 0))
        if hasattr(self, 'sidebar_co2_gauge'):
            co2_val = sensor_data.get("co2", 0)
            self.sidebar_co2_gauge.setValue(co2_val // 20)
            self.sidebar_co2_value_label.setText(f"{co2_val} ppm")
        if hasattr(self, 'sidebar_tvoc_gauge'):
            tvoc_val = sensor_data.get("tvoc", 0)
            self.sidebar_tvoc_gauge.setValue(min(tvoc_val // 10, 100))
            self.sidebar_tvoc_value_label.setText(f"{tvoc_val} ppb")
        if hasattr(self, 'sidebar_hum_gauge'):
            hum_val = sensor_data.get("hum", 0)
            self.sidebar_hum_gauge.setValue(int(hum_val))
            self.sidebar_hum_value_label.setText(f"{hum_val:.1f}%")
        if hasattr(self, 'sidebar_lux_gauge'):
            lux_val = sensor_data.get("lux", 0)
            self.sidebar_lux_gauge.setValue(min(int(lux_val) // 20, 100))
            self.sidebar_lux_value_label.setText(f"{int(lux_val)} lux")

    def _setup_device_toggles(self):
        """Tombol ON/OFF perangkat (UV, Lampu, Humidifier, Pump)."""
        self.device_buttons_container = QWidget()
        self.device_buttons_container.setObjectName("device-buttons-container")
        layout = QHBoxLayout(self.device_buttons_container)
        layout.setSpacing(18)
        layout.setContentsMargins(10, 10, 10, 10)

        def create_toggle(label_text, cmd):
            vbox = QVBoxLayout()
            vbox.setAlignment(Qt.AlignCenter)
            label = QLabel(label_text)
            label.setObjectName("toggle-label")
            switch = SlideSwitch()
            switch.setChecked(False)  # Start with OFF state
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
        self.main_content_layout.addWidget(self.device_buttons_container)

    def _setup_sliders(self):
        """Slider PWM untuk perangkat (kipas, lampu, dll)."""
        self.sliders_container = QWidget()
        self.sliders_container.setObjectName("sliders-container")
        layout = QGridLayout(self.sliders_container)
        layout.setSpacing(16)
        layout.setContentsMargins(10, 10, 10, 10)

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
            layout.addWidget(widget, row, col)
            self.control_widgets.append(slider)

        create_slider("Kipas Peltier", "P", 0, 0)
        create_slider("Kipas Radiator", "R", 0, 1)
        create_slider("Peltier PWM", "D", 1, 0)
        create_slider("Grow Light (Merah)", "G", 1, 1)
        create_slider("Grow Light (Biru)", "B", 2, 0)
        self.main_content_layout.addWidget(self.sliders_container)

    def _setup_sidebar_gauges(self):
        """Sidebar gauge sensor (temperature, CO2, TVOC, humidity, lux)."""
        self.sidebar_gauges_container = QWidget()
        self.sidebar_gauges_container.setObjectName("sidebar-gauges-container")
        self.sidebar_gauges_container.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(self.sidebar_gauges_container)
        sidebar_layout.setSpacing(12)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)

        def create_strip_gauge_box(label_text, obj_name_prefix):
            box = QWidget()
            box.setObjectName("gauge-box")
            layout = QVBoxLayout(box)
            label = QLabel(label_text)
            label.setProperty("sensor-label", True)
            layout.addWidget(label, alignment=Qt.AlignCenter)
            gauge = StripGauge()
            layout.addWidget(gauge)
            value_label = QLabel("N/A")
            value_label.setObjectName("gauge-value-label")
            layout.addWidget(value_label, alignment=Qt.AlignCenter)
            setattr(self, f"sidebar_{obj_name_prefix}_gauge", gauge)
            setattr(self, f"sidebar_{obj_name_prefix}_value_label", value_label)
            return box

        # Gauge suhu (half circle)
        temp_box = QWidget()
        temp_box.setObjectName("gauge-box")
        temp_layout = QVBoxLayout(temp_box)
        temp_label = QLabel("🌡️ Temperature")
        temp_label.setProperty("sensor-label", True)
        temp_layout.addWidget(temp_label, alignment=Qt.AlignCenter)
        self.sidebar_temp_gauge = HalfCircleGauge()
        temp_layout.addWidget(self.sidebar_temp_gauge)
        sidebar_layout.addWidget(temp_box)

        # Gauge strip lain
        sidebar_layout.addWidget(create_strip_gauge_box("🟢 CO₂ (ppm)", "co2"))
        sidebar_layout.addWidget(create_strip_gauge_box("🧪 TVOC (ppb)", "tvoc"))
        sidebar_layout.addWidget(create_strip_gauge_box("💧 Humidity (%)", "hum"))
        sidebar_layout.addWidget(create_strip_gauge_box("💡 Lux", "lux"))
        sidebar_layout.addStretch()

    def _debug_update_gauges(self):
        """Update sidebar gauges with random values for debugging."""
        sensor_data = {
            "temp": temp,
            "co2": co2,
            "tvoc": tvoc,
            "hum": hum,
            "lux": lux
        }
        self.update_gauges_from_dict(sensor_data)
