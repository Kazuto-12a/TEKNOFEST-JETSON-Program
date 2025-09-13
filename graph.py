import sys, time, random
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from datetime import datetime

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 Combined Environment Graph")
        self.resize(950, 600)

        self.timestamps, self.temp_data, self.hum_data, self.lux_data = [], [], [], []

        container = QWidget()
        layout = QVBoxLayout(container)

        # --- Main plot with left axis ---
        self.plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setTitle("🌡 Temp + 💧 Humidity + 💡 Lux", color="#ffffff", size="14pt")

        # Style left axis
        self.plot.getAxis("left").setTextPen("#b0bec5")
        self.plot.getAxis("bottom").setTextPen("#b0bec5")
        self.plot.getAxis("left").setPen("#414c50")
        self.plot.getAxis("bottom").setPen("#414c50")
        self.plot.getAxis("left").setTicks([[(i/5, f"{i/5:.1f}") for i in range(6)]])
        self.plot.getAxis("left").setLabel("🌡 Temperature (°C) / 💧 Humidity (%)", color="#ff9800")

        # Add right axis for Lux
        self.right_axis = pg.AxisItem("right")
        self.right_axis.setTextPen("#b0bec5")
        self.right_axis.setPen("#414c50")
        self.right_axis.setTicks([[(i/5, f"{i/5:.1f}") for i in range(6)]])
        self.right_axis.setLabel("💡 Lux (lx)", color="#ffeb3b")
        self.plot.getPlotItem().layout.addItem(self.right_axis, 2, 2)

        # Create second ViewBox for Lux
        self.vb2 = pg.ViewBox()
        self.plot.scene().addItem(self.vb2)
        self.right_axis.linkToView(self.vb2)
        self.vb2.setXLink(self.plot)

        # Keep views aligned
        self.plot.getViewBox().sigResized.connect(self.update_views)

        layout.addWidget(self.plot)
        self.setCentralWidget(container)

        # --- Lines ---
        self.temp_line = self.plot.plot(pen=pg.mkPen("#ff9800", width=3))   # orange
        self.hum_line = self.plot.plot(pen=pg.mkPen("#00e5ff", width=3))   # cyan
        self.lux_line = pg.PlotCurveItem(pen=pg.mkPen("#ffeb3b", width=3)) # yellow
        self.vb2.addItem(self.lux_line)

        # Floating labels
        self.temp_label = pg.TextItem(color="#ff9800", anchor=(0,1), fill="#192428AA")
        self.hum_label = pg.TextItem(color="#00e5ff", anchor=(0,1), fill="#192428AA")
        self.lux_label = pg.TextItem(color="#ffeb3b", anchor=(0,1), fill="#192428AA")
        for lbl in [self.temp_label, self.hum_label, self.lux_label]:
            self.plot.addItem(lbl)

        # Timer (simulate data)
        self.timer = QTimer()
        self.timer.timeout.connect(self.add_data)
        self.timer.start(2000)

    def update_views(self):
        self.vb2.setGeometry(self.plot.getViewBox().sceneBoundingRect())
        self.vb2.linkedViewChanged(self.plot.getViewBox(), self.vb2.XAxis)

    def normalize(self, data):
        if not data:
            return []
        mn, mx = min(data), max(data)
        if mx == mn:
            return [0.5 for _ in data]
        return [(v - mn) / (mx - mn) for v in data]

    def add_data(self):
        now = time.time()
        self.timestamps.append(now)
        self.temp_data.append(random.uniform(20, 35))   # °C
        self.hum_data.append(random.uniform(40, 80))    # %
        self.lux_data.append(random.uniform(200, 1000)) # lx
        self.update_plot()

    def update_plot(self):
        if not self.timestamps:
            return

        x = self.timestamps
        y_temp = self.normalize(self.temp_data)
        y_hum = self.normalize(self.hum_data)
        y_lux = self.normalize(self.lux_data)

        # Update lines
        self.temp_line.setData(x, y_temp)
        self.hum_line.setData(x, y_hum)
        self.lux_line.setData(x, y_lux)

        # Update labels
        if x:
            self.temp_label.setText(f"{self.temp_data[-1]:.1f}°C")
            self.temp_label.setPos(x[-1], y_temp[-1])
            self.hum_label.setText(f"{self.hum_data[-1]:.1f}%")
            self.hum_label.setPos(x[-1], y_hum[-1])
            self.lux_label.setText(f"{self.lux_data[-1]:.0f} lx")
            self.lux_label.setPos(x[-1], y_lux[-1])

        # Keep X range tight
        self.plot.setXRange(min(x), max(x))

# Run
app = QApplication(sys.argv)
pg.setConfigOption("background", "#2d383c")
pg.setConfigOption("foreground", "#ffffff")
w = MainWindow()
w.show()
sys.exit(app.exec_())
