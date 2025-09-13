import serial
import serial.tools.list_ports
from PySide6.QtCore import Qt, Signal, QTimer, QRect, QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QFrame

class Notification(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground); self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.animation = QPropertyAnimation(self, b"geometry"); self.animation.setDuration(500); self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.label = QLabel(self); layout = QVBoxLayout(self); layout.addWidget(self.label); self.setLayout(layout)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.hide_smoothly)
    def set_message(self, message, level="info"):
        self.label.setText(message)
        if level == "success": self.setStyleSheet("background-color: rgba(0, 128, 0, 0.85); color: white; border-radius: 10px; padding: 15px; font-size: 14px;")
        elif level == "error": self.setStyleSheet("background-color: rgba(176, 0, 0, 0.85); color: white; border-radius: 10px; padding: 15px; font-size: 14px;")
        else: self.setStyleSheet("background-color: rgba(40, 40, 40, 0.85); color: white; border-radius: 10px; padding: 15px; font-size: 14px;")
    def show_notification(self, message, level="info", duration=3000):
        if not self.parent(): return
        self.set_message(message, level); parent_geometry = self.parent().geometry(); self.adjustSize()
        start_pos = QRect(parent_geometry.right(), parent_geometry.bottom() - self.height() - 20, self.width(), self.height())
        end_pos = QRect(parent_geometry.right() - self.width() - 20, parent_geometry.bottom() - self.height() - 20, self.width(), self.height())
        self.setGeometry(start_pos); self.show()
        self.animation.setStartValue(start_pos); self.animation.setEndValue(end_pos); self.animation.start()
        self.timer.start(duration)
    def hide_smoothly(self):
        start_pos = self.geometry(); end_pos = QRect(self.parent().geometry().right(), start_pos.y(), start_pos.width(), start_pos.height())
        self.animation.setStartValue(start_pos); self.animation.setEndValue(end_pos); self.animation.finished.connect(self.hide); self.animation.start()

class Settings(QWidget):
    ser = None
    connection_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setObjectName("settings-container")
        layout = QVBoxLayout(self); layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        serial_container = QWidget(); serial_container.setObjectName("serial-container"); serial_container.setMaximumWidth(600)
        serial_layout = QHBoxLayout(serial_container); serial_layout.addWidget(QLabel("Serial Port:"))
        self.serial_combo = QComboBox(); serial_layout.addWidget(self.serial_combo, 1)
        self.refresh_btn = QPushButton("Refresh"); serial_layout.addWidget(self.refresh_btn)
        self.connect_btn = QPushButton("Connect"); self.connect_btn.setObjectName("connect-btn"); serial_layout.addWidget(self.connect_btn)
        layout.addWidget(serial_container)
        self.refresh_btn.clicked.connect(self.refresh_serial_ports)
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.notification_popup = Notification(self.window())
        self.refresh_serial_ports()

    def toggle_connection(self):
        if Settings.ser and Settings.ser.is_open:
            self.disconnect_serial_port()
        else:
            self.connect_serial_port()

    def connect_serial_port(self):
        port = self.serial_combo.currentText()
        if not port or "Tidak ada port" in port:
            self.notification_popup.show_notification("Tidak ada port serial yang dipilih.", "error")
            return
        try:
            print(f"Mencoba menghubungkan ke {port}...")
            Settings.ser = serial.Serial(port, 115200, timeout=1)
            print(f"Berhasil terhubung ke {port}")
            self.notification_popup.show_notification(f"Berhasil terhubung ke {port}", "success")
            self.connect_btn.setText("Disconnect"); self.connect_btn.setStyleSheet("background-color: #c0392b;")
            self.connection_changed.emit(True)
        except serial.SerialException as e:
            print(f"Gagal terhubung: {e}"); self.notification_popup.show_notification(f"Gagal terhubung: {e}", "error")
            Settings.ser = None; self.connection_changed.emit(False)

    def disconnect_serial_port(self):
        if Settings.ser and Settings.ser.is_open:
            Settings.ser.close()
            print("Koneksi serial ditutup.")
        self.connect_btn.setText("Connect"); self.connect_btn.setStyleSheet("")
        self.connection_changed.emit(False); Settings.ser = None

    def refresh_serial_ports(self):
        self.serial_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if not ports: self.serial_combo.addItem("Tidak ada port")
        else: self.serial_combo.addItems(ports)

    @staticmethod
    def send_command(cmd: str):
        if Settings.ser and Settings.ser.is_open:
            try:
                print(f"[SERIAL] Mengirim: {cmd.strip()}"); Settings.ser.write(cmd.encode('utf-8'))
            except Exception as e: print(f"Error saat menulis ke serial: {e}")
        else: print(f"[SERIAL] GAGAL: Port tidak terhubung. Perintah '{cmd.strip()}' tidak dikirim.")

    @staticmethod
    def read_data():
        if Settings.ser and Settings.ser.is_open:
            try:
                line = Settings.ser.readline().decode('utf-8', errors='ignore').strip()
                if line: print(f"[SERIAL] Menerima: {line}")
                return line
            except Exception as e: print(f"Error saat membaca dari serial: {e}")
        return None

    @staticmethod
    def is_connected():
        return Settings.ser is not None and Settings.ser.is_open