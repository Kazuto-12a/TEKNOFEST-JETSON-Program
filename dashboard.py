from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QTextEdit
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QPixmap, QTextCursor
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import requests
import os
import time
import random
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG_LOG_TERMINAL = True  # Set True to show real terminal output in system log

class QTextEditLogger:
    def __init__(self, text_edit):
        self.text_edit = text_edit
        self._stdout = sys.stdout
        self._stderr = sys.stderr
    def write(self, msg):
        if msg.strip():
            color = None
            lower = msg.lower()
            if "success" in lower:
                color = "#81c784"  # Green
            elif "warning" in lower:
                color = "#ffd600"  # Yellow
            elif "error" in lower:
                color = "#e57373"  # Red
            if color:
                html = f'<span style="color:{color};">{msg.rstrip()}</span>'
                self.text_edit.append(html)
            else:
                self.text_edit.append(msg.rstrip())
            self.text_edit.moveCursor(QTextCursor.End)
    def flush(self):
        pass
    def restore(self):
        sys.stdout = self._stdout
        sys.stderr = self._stderr

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("menu-box")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # --- TOP BAR (Greeting, Time, Date, Temp) ---
        top_bar = QWidget()
        top_bar.setObjectName("dashboard-topbar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(32, 24, 32, 24)
        top_bar_layout.setSpacing(32)

        # LEFT: Greeting & subtext
        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        self.greeting_label = QLabel("Hi, R2C! Good Evening...")
        self.greeting_label.setObjectName("dashboard-greeting")
        self.greeting_label.setStyleSheet("color: #222;")
        self.subtext_label = QLabel("Welcome Home.")
        self.subtext_label.setObjectName("dashboard-subtext")
        self.subtext_label.setStyleSheet("color: #444;")
        left_col.addWidget(self.greeting_label)
        left_col.addWidget(self.subtext_label)
        left_col.addStretch()

        # CENTER: Time & Date
        center_col = QVBoxLayout()
        center_col.setSpacing(4)
        self.time_label = QLabel()
        self.time_label.setObjectName("dashboard-time")
        self.time_label.setStyleSheet("color: #192428; font-weight: bold;")
        self.date_label = QLabel()
        self.date_label.setObjectName("dashboard-date")
        self.date_label.setStyleSheet("color: #444;")
        center_col.addWidget(self.time_label, alignment=Qt.AlignRight)
        center_col.addWidget(self.date_label, alignment=Qt.AlignRight)
        center_col.addStretch()

        # RIGHT: Temperature
        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        self.temp_label = QLabel()
        self.temp_label.setObjectName("dashboard-temp")
        self.temp_label.setStyleSheet("color: #192428; font-weight: bold;")
        right_col.addWidget(self.temp_label, alignment=Qt.AlignRight)
        right_col.addStretch()

        top_bar_layout.addLayout(left_col, 2)
        top_bar_layout.addLayout(center_col, 1)
        top_bar_layout.addLayout(right_col, 1)

        # Set background image via stylesheet (dynamic path)
        wallpaper_path = os.path.join(BASE_DIR, 'wallpaper3.jpg').replace('\\', '/')
        top_bar.setStyleSheet(f"""
            QWidget#dashboard-topbar {{
                background-color: #3a5a7a;
                background-image: url("{wallpaper_path}");
                background-position: center;
                background-repeat: no-repeat;
                border-radius: 20px;
                border: 3px solid #223344;
            }}
        """)

        # --- LOGO CARD ---
        logo_card = QWidget()
        logo_card.setObjectName("dashboard-logo-card")
        logo_card_layout = QHBoxLayout(logo_card)
        logo_card_layout.setContentsMargins(24, 16, 24, 16)
        logo_card_layout.setSpacing(16)

        logo_label = QLabel()
        logo_label.setObjectName("dashboard-logo")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(os.path.join(BASE_DIR, "UKSW.png"))
        logo_label.setPixmap(logo_pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        logo_text = QLabel("R2C SWCU")
        logo_text.setObjectName("dashboard-logo-text")
        logo_text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        logo_card_layout.addWidget(logo_label)
        logo_card_layout.addWidget(logo_text)

        # --- TOP ROW (Topbar + Logo Card) ---
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(16)
        top_row.addWidget(top_bar, 3)
        top_row.addWidget(logo_card, 2)

        main_layout.addLayout(top_row)

        # --- MAIN CONTENT ---
        main_content = QWidget()
        main_content.setObjectName("main-content")
        main_content.setMinimumHeight(280)
        main_content_layout = QHBoxLayout(main_content)
        main_content_layout.setContentsMargins(32, 32, 32, 32)
        main_content_layout.setSpacing(16)

        # Kiri: Container khusus untuk grafik
        graph_container = QWidget()
        graph_container.setObjectName("dashboard-graph-frame")
        graph_container.setMinimumWidth(320)
        graph_container.setMaximumWidth(420)
        graph_container.setMinimumHeight(140)
        graph_container.setMaximumHeight(220)
        graph_container_layout = QVBoxLayout(graph_container)
        graph_container_layout.setContentsMargins(10, 10, 10, 18)
        graph_container_layout.setSpacing(0)
        # --- PlotWidget dengan axis kanan (Lux) dan floating label ---
        class TimeAxisItem(pg.AxisItem):
            def tickStrings(self, values, scale, spacing):
                labels = []
                for v in values:
                    try:
                        if v > 0:
                            labels.append(datetime.fromtimestamp(v).strftime("%H:%M"))
                        else:
                            labels.append("")
                    except Exception:
                        labels.append("")
                return labels
        self.plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setTitle("<span style='font-size:12pt;color:#fff;'>🌡 Temp + 💧 Humidity + <span style='color:#ffeb3b;'>💡 Lux</span></span>")
        self.plot.getAxis("right").setTextPen(pg.mkPen("#ffeb3b", width=2))
        self.plot.getAxis("right").setLabel("<span style='color:#ffeb3b;font-weight:bold;'>💡 Lux (lx)</span>")
        self.plot.getAxis("left").setTextPen("#b0bec5")
        self.plot.getAxis("bottom").setTextPen("#b0bec5")
        self.plot.getAxis("left").setPen("#414c50")
        self.plot.getAxis("bottom").setPen("#414c50")
        self.plot.getAxis("left").setTicks([[(i/5, f"{i/5:.1f}") for i in range(6)]])
        self.plot.getAxis("left").setLabel("🌡 Temperature (°C) / 💧 Humidity (%)", color="#ff9800")
        # Axis kanan untuk Lux
        self.right_axis = pg.AxisItem("right")
        self.right_axis.setTextPen("#b0bec5")
        self.right_axis.setPen("#414c50")
        self.right_axis.setTicks([[(i/5, f"{i/5:.1f}") for i in range(6)]])
        self.right_axis.setLabel("💡 Lux (lx)", color="#ffeb3b")
        self.plot.getPlotItem().layout.addItem(self.right_axis, 2, 2)
        # ViewBox kedua untuk Lux
        self.vb2 = pg.ViewBox()
        self.plot.scene().addItem(self.vb2)
        self.right_axis.linkToView(self.vb2)
        self.vb2.setXLink(self.plot)
        self.plot.getViewBox().sigResized.connect(self.update_views)
        graph_container_layout.addWidget(self.plot)

        # Kanan: Container log (biru, border sama dengan lain)
        log_container = QWidget()
        log_container.setObjectName("dashboard-log-frame")
        log_container.setMinimumWidth(340)
        log_container.setMaximumWidth(420)
        log_container.setMinimumHeight(340)
        log_container.setMaximumHeight(600)
        log_container.setStyleSheet("background:#26343c; border:2px solid #39ace7; border-radius:12px;")
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(18, 18, 18, 18)
        log_layout.setSpacing(10)
        # Label System Log (kuning, margin top)
        log_label = QLabel("System Log")
        log_label.setObjectName("dashboard-log-label")
        log_label.setStyleSheet("background:#26343c; color:#ffd600; font-size:16px; font-weight:bold; border:2px solid #ffd600; border-radius:6px; padding:6px 0px; margin-top:12px; qproperty-alignment:'AlignCenter';")
        log_layout.addWidget(log_label)
        # Area log terminal (hijau)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setObjectName("dashboard-log-text")
        self.log_text.setStyleSheet("background:#192428; color:#81c784; border:2px solid #81c784; border-radius:8px; font-family:Consolas,monospace; font-size:13px;")
        self.log_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        log_layout.addWidget(self.log_text, 1)
        if DEBUG_LOG_TERMINAL:
            self.logger = QTextEditLogger(self.log_text)
            sys.stdout = self.logger
            sys.stderr = self.logger
        else:
            # Mockup log
            self.mockup_logs = [
                "[INFO] System initialized",
                "[INFO] Connecting to MQTT...",
                "[SUCCESS] MQTT Connected",
                "[INFO] Reading sensor data...",
                "[ERROR] Sensor timeout",
                "[INFO] Retrying sensor read...",
                "[SUCCESS] Sensor data received",
                "[INFO] Updating dashboard...",
                "[INFO] System running normally"
            ]
            self.mockup_log_index = 0
            self.log_text.append(self.mockup_logs[0])
            # Timer untuk update mockup log
            self.log_timer = QTimer(self)
            self.log_timer.timeout.connect(self.update_mockup_log)
            self.log_timer.start(2000)

        # Layout horizontal: grafik kiri, log kanan
        main_content_layout.addWidget(graph_container, alignment=Qt.AlignTop | Qt.AlignLeft)
        main_content_layout.addWidget(log_container, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Data dan line
        self.timestamps, self.temp_data, self.hum_data, self.lux_data = [], [], [], []
        self.temp_line = self.plot.plot(pen=pg.mkPen("#ff9800", width=3))
        self.hum_line = self.plot.plot(pen=pg.mkPen("#00e5ff", width=3))
        self.lux_line = pg.PlotCurveItem(pen=pg.mkPen("#ffeb3b", width=3))
        self.vb2.addItem(self.lux_line)
        # Floating labels
        self.temp_label = pg.TextItem(color="#ff9800", anchor=(0,1), fill="#192428AA")
        self.hum_label = pg.TextItem(color="#00e5ff", anchor=(0,1), fill="#192428AA")
        self.lux_label = pg.TextItem(color="#ffeb3b", anchor=(0,1), fill="#192428AA")
        for lbl in [self.temp_label, self.hum_label, self.lux_label]:
            self.plot.addItem(lbl)

        # Timer update data dummy
        # self.graph_timer = QTimer(self)
        # self.graph_timer.timeout.connect(self.add_graph_data)
        # self.graph_timer.start(2000)

        # Hapus placeholder jika grafik sudah tampil
        # main_content_layout.addWidget(placeholder)

        main_layout.addWidget(main_content, 1)

        # --- Timers ---
        timer_datetime = QTimer(self)
        timer_datetime.timeout.connect(self.update_datetime)
        timer_datetime.start(1000)
        self.update_datetime()

        timer_temp = QTimer(self)
        timer_temp.timeout.connect(self.update_temperature)
        timer_temp.start(600000)
        self.update_temperature()

    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.date_label.setText(now.toString("dddd, dd MMMM yyyy"))
        self.time_label.setText(now.toString("HH:mm:ss"))

    def update_temperature(self):
        lat, lon = 41.0, 28.9
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            response = requests.get(url, timeout=5)
            data = response.json()
            temp = data["current_weather"]["temperature"]
            self.temp_label.setText(f"🌡️ {temp}°C")
        except Exception:
            self.temp_label.setText("🌡️ N/A")

    def add_graph_data(self):
        now = time.time()
        self.timestamps.append(now)
        self.temp_data.append(random.uniform(20, 35))
        self.hum_data.append(random.uniform(40, 80))
        self.lux_data.append(random.uniform(200, 1000))
        self.update_graph()

    def update_views(self):
        self.vb2.setGeometry(self.plot.getViewBox().sceneBoundingRect())
        self.vb2.linkedViewChanged(self.plot.getViewBox(), self.vb2.XAxis)

    def update_graph(self):
        if not self.timestamps:
            return
        x = self.timestamps
        y_temp = self.normalize(self.temp_data)
        y_hum = self.normalize(self.hum_data)
        y_lux = self.normalize(self.lux_data)
        self.temp_line.setData(x, y_temp)
        self.hum_line.setData(x, y_hum)
        self.lux_line.setData(x, y_lux)
        # Floating labels
        if x:
            self.temp_label.setText(f"{self.temp_data[-1]:.1f}°C")
            self.temp_label.setPos(x[-1], y_temp[-1])
            self.hum_label.setText(f"{self.hum_data[-1]:.1f}%")
            self.hum_label.setPos(x[-1], y_hum[-1])
            self.lux_label.setText(f"{self.lux_data[-1]:.0f} lx")
            self.lux_label.setPos(x[-1], y_lux[-1])
        self.plot.setXRange(min(x), max(x))
        self.vb2.setXRange(min(x), max(x))

    def normalize(self, data):
        if not data:
            return []
        mn, mx = min(data), max(data)
        if mx == mn:
            return [0.5 for _ in data]
        return [(v - mn) / (mx - mn) for v in data]

    def update_mockup_log(self):
        self.mockup_log_index = (self.mockup_log_index + 1) % len(self.mockup_logs)
        self.log_text.append(self.mockup_logs[self.mockup_log_index])
        self.log_text.moveCursor(QTextCursor.End)

    def update_sensor_data(self, temp, hum, lux, eco2, tvoc, timestamp=None):
        """Update the graph with new sensor data. Optionally use provided timestamp."""
        now = timestamp if timestamp is not None else time.time()
        self.timestamps.append(now)
        self.temp_data.append(temp)
        self.hum_data.append(hum)
        self.lux_data.append(lux)
        self.update_graph()
