import json
import random
import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, Slot, QTimer
from gauges import HalfCircleGauge, StripGauge
from settings import Settings
from slide_switch import SlideSwitch


DEBUG_GAUGE = True  # Set True to test gauge with random data


class Sensors(QWidget):
    def __init__(self, dashboard_widget=None):
        super().__init__()
        self.setObjectName("sensors-container")
        self.control_widgets = []
        self.dashboard_widget = dashboard_widget

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

        # Tambahkan temperature gauges ke main content
        self._setup_temp_gauges_and_sensor_gauges()

        # Sidebar gauges
        # self._setup_sidebar_gauges()  # Commented out as per the new design

        # Tambahkan ke layout utama
        main_layout.addWidget(self.main_content, 2)
        main_layout.addStretch()

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

    def update_gauges_from_dict(self, sensor_data, is_internal=False):
        """Update sensor gauges from dict. If is_internal=True, update internal sensors, else external."""
        if is_internal:
            # Internal sensors
            int_temp = sensor_data.get("temp", 0)
            if hasattr(self, 'internal_temp_gauge'):
                self.internal_temp_gauge.setTemperature(int_temp)
            if hasattr(self, 'int_co2_gauge'):
                self.int_co2_gauge.setValue(sensor_data.get("co2", 0) // 20)
                self.int_co2_value_label.setText(f"{sensor_data.get('co2', 0)} ppm")
            if hasattr(self, 'int_tvoc_gauge'):
                self.int_tvoc_gauge.setValue(min(int(sensor_data.get("tvoc", 0)) // 10, 100))
                self.int_tvoc_value_label.setText(f"{sensor_data.get('tvoc', 0)} ppb")
            if hasattr(self, 'int_hum_gauge'):
                self.int_hum_gauge.setValue(int(sensor_data.get("hum", 0)))
                self.int_hum_value_label.setText(f"{sensor_data.get('hum', 0):.1f}%")
            if hasattr(self, 'int_lux_gauge'):
                self.int_lux_gauge.setValue(min(int(sensor_data.get("lux", 0)) // 20, 100))
                self.int_lux_value_label.setText(f"{int(sensor_data.get('lux', 0))} lux")
        else:
            # External sensors
            ext_temp = sensor_data.get("temp", 0)
            if hasattr(self, 'external_temp_gauge'):
                self.external_temp_gauge.setTemperature(ext_temp)
            if hasattr(self, 'ext_co2_gauge'):
                self.ext_co2_gauge.setValue(sensor_data.get("co2", 0) // 20)
                self.ext_co2_value_label.setText(f"{sensor_data.get('co2', 0)} ppm")
            if hasattr(self, 'ext_tvoc_gauge'):
                self.ext_tvoc_gauge.setValue(min(int(sensor_data.get("tvoc", 0)) // 10, 100))
                self.ext_tvoc_value_label.setText(f"{sensor_data.get('tvoc', 0)} ppb")
            if hasattr(self, 'ext_hum_gauge'):
                self.ext_hum_gauge.setValue(int(sensor_data.get("hum", 0)))
                self.ext_hum_value_label.setText(f"{sensor_data.get('hum', 0):.1f}%")
            if hasattr(self, 'ext_lux_gauge'):
                self.ext_lux_gauge.setValue(min(int(sensor_data.get("lux", 0)) // 20, 100))
                self.ext_lux_value_label.setText(f"{int(sensor_data.get('lux', 0))} lux")

    def _setup_temp_gauges_and_sensor_gauges(self):
        """Add two temperature gauges (External/Green, Internal/Red) to main content area, inside a styled container."""
        # Outer frame for visual separation
        temp_frame = QFrame()
        temp_frame.setObjectName("temp-gauges-frame")
        temp_frame.setFrameShape(QFrame.StyledPanel)
        temp_frame.setStyleSheet("""
            QFrame#temp-gauges-frame {
                border: 2px solid #3ec6ff;
                border-radius: 18px;
                background: #232c33;
                margin-top: 8px;
                margin-bottom: 8px;
            }
        """)
        temp_frame_layout = QVBoxLayout(temp_frame)
        temp_frame_layout.setContentsMargins(16, 16, 16, 16)
        temp_frame_layout.setSpacing(18)

        # External
        ext_box = QWidget()
        ext_layout = QVBoxLayout(ext_box)
        ext_layout.setSpacing(8)
        ext_label = QLabel("\U0001F321\ufe0f <span style='color:#00FF00;font-weight:bold;'>External Temp</span>")
        ext_label.setProperty("sensor-label", True)
        ext_label.setTextFormat(Qt.RichText)
        ext_layout.addWidget(ext_label, alignment=Qt.AlignCenter)
        self.external_temp_gauge = HalfCircleGauge()
        self.external_temp_gauge.setMinimumSize(260, 160)
        self.external_temp_gauge.setStyleSheet("color: white;")
        ext_layout.addWidget(self.external_temp_gauge)
        # External sensor gauges
        self.ext_sensor_gauges = self._create_sensor_gauges_group("ext")
        ext_layout.addWidget(self.ext_sensor_gauges)
        temp_frame_layout.addWidget(ext_box)

        # Internal
        int_box = QWidget()
        int_layout = QVBoxLayout(int_box)
        int_layout.setSpacing(8)
        int_label = QLabel("\U0001F321\ufe0f <span style='color:#FF0000;font-weight:bold;'>Internal Temp</span>")
        int_label.setProperty("sensor-label", True)
        int_label.setTextFormat(Qt.RichText)
        int_layout.addWidget(int_label, alignment=Qt.AlignCenter)
        self.internal_temp_gauge = HalfCircleGauge()
        self.internal_temp_gauge.setMinimumSize(260, 160)
        self.internal_temp_gauge.setStyleSheet("color: white;")
        int_layout.addWidget(self.internal_temp_gauge)
        # Internal sensor gauges
        self.int_sensor_gauges = self._create_sensor_gauges_group("int")
        int_layout.addWidget(self.int_sensor_gauges)
        temp_frame_layout.addWidget(int_box)

        self.main_content_layout.addWidget(temp_frame)

    def _create_sensor_gauges_group(self, prefix):
        group = QWidget()
        layout = QHBoxLayout(group)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        # CO2
        co2 = StripGauge()
        co2_label = QLabel("\U0001F7E2 CO (ppm)")
        co2_label.setProperty("sensor-label", True)
        co2_val = QLabel("N/A")
        co2_val.setObjectName("gauge-value-label")
        vbox1 = QVBoxLayout()
        vbox1.addWidget(co2_label, alignment=Qt.AlignCenter)
        vbox1.addWidget(co2)
        vbox1.addWidget(co2_val, alignment=Qt.AlignCenter)
        layout.addLayout(vbox1)
        # TVOC
        tvoc = StripGauge()
        tvoc_label = QLabel("\U0001F9EA TVOC (ppb)")
        tvoc_label.setProperty("sensor-label", True)
        tvoc_val = QLabel("N/A")
        tvoc_val.setObjectName("gauge-value-label")
        vbox2 = QVBoxLayout()
        vbox2.addWidget(tvoc_label, alignment=Qt.AlignCenter)
        vbox2.addWidget(tvoc)
        vbox2.addWidget(tvoc_val, alignment=Qt.AlignCenter)
        layout.addLayout(vbox2)
        # Humidity
        hum = StripGauge()
        hum_label = QLabel("\U0001F4A7 Humidity (%)")
        hum_label.setProperty("sensor-label", True)
        hum_val = QLabel("N/A")
        hum_val.setObjectName("gauge-value-label")
        vbox3 = QVBoxLayout()
        vbox3.addWidget(hum_label, alignment=Qt.AlignCenter)
        vbox3.addWidget(hum)
        vbox3.addWidget(hum_val, alignment=Qt.AlignCenter)
        layout.addLayout(vbox3)
        # Lux
        lux = StripGauge()
        lux_label = QLabel("\U0001F4A1 Lux")
        lux_label.setProperty("sensor-label", True)
        lux_val = QLabel("N/A")
        lux_val.setObjectName("gauge-value-label")
        vbox4 = QVBoxLayout()
        vbox4.addWidget(lux_label, alignment=Qt.AlignCenter)
        vbox4.addWidget(lux)
        vbox4.addWidget(lux_val, alignment=Qt.AlignCenter)
        layout.addLayout(vbox4)
        # Save references
        setattr(self, f"{prefix}_co2_gauge", co2)
        setattr(self, f"{prefix}_co2_value_label", co2_val)
        setattr(self, f"{prefix}_tvoc_gauge", tvoc)
        setattr(self, f"{prefix}_tvoc_value_label", tvoc_val)
        setattr(self, f"{prefix}_hum_gauge", hum)
        setattr(self, f"{prefix}_hum_value_label", hum_val)
        setattr(self, f"{prefix}_lux_gauge", lux)
        setattr(self, f"{prefix}_lux_value_label", lux_val)
        return group

    def _debug_update_gauges(self):
        """Update both external and internal sensor gauges with separate random values for debugging."""
        now = time.time()
        # External random values
        ext_data = {
            "temp": random.uniform(20, 30),
            "co2": random.randint(400, 2000),
            "tvoc": random.randint(0, 600),
            "hum": random.uniform(30, 80),
            "lux": random.randint(0, 2000)
        }
        # Internal random values
        int_data = {
            "temp": random.uniform(25, 40),
            "co2": random.randint(400, 2000),
            "tvoc": random.randint(0, 600),
            "hum": random.uniform(30, 80),
            "lux": random.randint(0, 2000)
        }
        # Set external gauges
        self.external_temp_gauge.setTemperature(ext_data["temp"])
        self.ext_co2_gauge.setValue(ext_data["co2"] // 20)
        self.ext_co2_value_label.setText(f"{ext_data['co2']} ppm")
        self.ext_tvoc_gauge.setValue(min(ext_data["tvoc"] // 10, 100))
        self.ext_tvoc_value_label.setText(f"{ext_data['tvoc']} ppb")
        self.ext_hum_gauge.setValue(int(ext_data["hum"]))
        self.ext_hum_value_label.setText(f"{ext_data['hum']:.1f}%")
        self.ext_lux_gauge.setValue(min(int(ext_data["lux"]) // 20, 100))
        self.ext_lux_value_label.setText(f"{int(ext_data['lux'])} lux")
        # Set internal gauges
        self.internal_temp_gauge.setTemperature(int_data["temp"])
        self.int_co2_gauge.setValue(int_data["co2"] // 20)
        self.int_co2_value_label.setText(f"{int_data['co2']} ppm")
        self.int_tvoc_gauge.setValue(min(int_data["tvoc"] // 10, 100))
        self.int_tvoc_value_label.setText(f"{int_data['tvoc']} ppb")
        self.int_hum_gauge.setValue(int(int_data["hum"]))
        self.int_hum_value_label.setText(f"{int_data['hum']:.1f}%")
        self.int_lux_gauge.setValue(min(int(int_data["lux"]) // 20, 100))
        self.int_lux_value_label.setText(f"{int(int_data['lux'])} lux")
        # Also update dashboard graph if available, with the external values
        if self.dashboard_widget:
            self.dashboard_widget.update_sensor_data(
                ext_data["temp"],
                ext_data["hum"],
                ext_data["lux"],
                ext_data["co2"],
                ext_data["tvoc"],
                timestamp=now
            )
