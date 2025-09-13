import os
import sys
import json
import paho.mqtt.client as mqtt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, QThread, Signal
from camera import Camera
from settings import Settings
from dashboard import Dashboard
from sensors import Sensors
from manual import Manual
from auto import Auto

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MqttClient(QObject):
    message_received = Signal(str)

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Worker: Terhubung ke Broker!")
            client.subscribe("sensor/data")
        else:
            print(f"MQTT Worker: Gagal terhubung, kode: {rc}")

    def on_message(self, client, userdata, msg):
        data = msg.payload.decode()
        self.message_received.emit(data)

    def run(self):
        print("MQTT Worker: Memulai koneksi...")
        try:
            self.client.connect("localhost", 1883, 60)
            self.client.loop_forever()
        except Exception as e:
            print(f"MQTT Worker: Error - {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(BASE_DIR, "Icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("R2C Smart Control UI")
        self.setGeometry(100, 100, 1280, 720)

        self.init_ui()
        self.init_mqtt()
        self.last_index = 0
        self.update_internal_from_json()

    def init_ui(self):
        # Central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Main widgets
        self.settings_widget = Settings()
        self.dashboard_widget = Dashboard()
        self.sensors_widget = Sensors(dashboard_widget=self.dashboard_widget)
        self.manual_widget = Manual()  # Manual page
        self.camera_widget = Camera()
        self.auto_widget = Auto()

        # Signal for enabling/disabling device controls
        self.settings_widget.connection_changed.connect(
            self.sensors_widget.set_controls_enabled
        )

        # Stacked widget for main content
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.dashboard_widget)  # 0
        self.stacked_widget.addWidget(self.sensors_widget)    # 1 (was devices)
        self.stacked_widget.addWidget(self.manual_widget)     # 2
        self.stacked_widget.addWidget(self.auto_widget)       # 3
        self.stacked_widget.addWidget(self.camera_widget)     # 4
        self.stacked_widget.addWidget(self.settings_widget)   # 5
        main_layout.addWidget(self.stacked_widget, 1)

    def init_mqtt(self):
        self.mqtt_thread = QThread()
        self.mqtt_worker = MqttClient()
        self.mqtt_worker.moveToThread(self.mqtt_thread)

        self.mqtt_thread.started.connect(self.mqtt_worker.run)
        self.mqtt_worker.message_received.connect(self.update_gui_with_mqtt_data)

        self.mqtt_thread.start()
        print("Main thread: Thread MQTT dimulai.")

    def update_gui_with_mqtt_data(self, message):
        """Slot: update dashboard with new MQTT data."""
        print(f"Main thread: Menerima data dari MQTT -> {message}")
        try:
            parts = message.split(',')
            if len(parts) == 5:
                temp = float(parts[0])
                hum = float(parts[1])
                lux = int(parts[2])
                eco2 = int(parts[3])
                tvoc = int(parts[4])
                print(f"Data Parsed -> Temp: {temp}, Hum: {hum}, Lux: {lux}, eCO2: {eco2}, TVOC: {tvoc}")
                self.dashboard_widget.update_sensor_data(temp, hum, lux, eco2, tvoc)
                sensor_data = {
                    "temp": temp,
                    "co2": eco2,
                    "tvoc": tvoc,
                    "hum": hum,
                    "lux": lux
                }
                self.sensors_widget.update_gauges_from_dict(sensor_data, is_internal=False)  # External
            else:
                print(f"Main thread: Format data tidak sesuai, jumlah bagian: {len(parts)}")
        except (ValueError, IndexError) as e:
            print(f"Main thread: Error saat mem-parse data: {e}")

    def update_internal_from_json(self):
        json_path = os.path.join(BASE_DIR, "sensor_values.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                self.sensors_widget.update_gauges_from_dict(data, is_internal=True)
            except Exception as e:
                print(f"Error loading internal sensor values: {e}")

    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 18, 12, 12)
        sidebar_layout.setSpacing(8)

        # Sidebar label and divider
        project_label = QLabel("SMART CONTROL")
        project_label.setObjectName("sidebar-label")
        sidebar_layout.addWidget(project_label)
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setObjectName("sidebar-divider")
        sidebar_layout.addWidget(divider)

        # Sidebar buttons
        btn_dashboard = QPushButton("  🏠  Dashboard")
        btn_sensors = QPushButton("  🖥️  Sensors")
        btn_manual = QPushButton("  🛠️  Manual")
        btn_auto = QPushButton("  🤖  Auto")
        btn_camera = QPushButton("  📸  Camera")
        btn_settings = QPushButton("  ⚙️  Settings")
        buttons = [btn_dashboard, btn_sensors, btn_manual, btn_auto, btn_camera, btn_settings]
        for btn in buttons:
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()

        # Button navigation langsung
        btn_dashboard.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        btn_sensors.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        btn_manual.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        btn_auto.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        btn_camera.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        btn_settings.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))
        btn_dashboard.setChecked(True)
        return sidebar

    def closeEvent(self, event):
        print("Menutup aplikasi...")
        if self.mqtt_thread.isRunning():
            print("Menghentikan thread MQTT...")
            self.mqtt_thread.quit()
            self.mqtt_thread.wait()
            print("Thread MQTT dihentikan.")
        self.camera_widget.cleanup()
        self.settings_widget.disconnect_serial_port()
        print("Semua koneksi dihentikan. Keluar.")
        event.accept()


def main():
    app = QApplication(sys.argv)
    style_path = os.path.join(BASE_DIR, "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()