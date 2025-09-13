import cv2
from PySide6.QtCore import QThread, Signal, QObject, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton

class CameraWorker(QObject):
    frame_ready = Signal(int, QImage)
    camera_error = Signal(int, str)

    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self._is_running = False
        self.cap = None

    def run(self):
        self._is_running = True
        print(f"Starting camera worker for index: {self.camera_index}")
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        for backend in backends:
            self.cap = cv2.VideoCapture(self.camera_index, backend)
            if self.cap.isOpened():
                break
        
        if not self.cap or not self.cap.isOpened():
            self.camera_error.emit(self.camera_index, "Cannot open camera")
            self._is_running = False
            return

        while self._is_running:
            ret, frame = self.cap.read()
            if not ret:
                self.camera_error.emit(self.camera_index, "No Signal")
                break
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_ready.emit(self.camera_index, qt_image.copy())

        if self.cap:
            self.cap.release()
        print(f"Stopping camera worker for index: {self.camera_index}")

    def stop(self):
        self._is_running = False

class Camera(QWidget):
    def __init__(self):
        super().__init__()
        # ... (sisa __init__ Anda tidak berubah)
        self.setObjectName("main-menu-container")
        main_layout = QVBoxLayout(self)
        self.camera_grid_layout = QHBoxLayout()
        main_layout.addLayout(self.camera_grid_layout)
        self.threads = {}
        self.workers = {}
        self.labels = {}
        self.buttons = {}
        self.add_camera_frame(0, "Kamera 1")
        self.add_camera_frame(1, "Kamera 2")

    def add_camera_frame(self, index, title):
        # ... (fungsi ini tidak berubah)
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFixedSize(420, 340)
        frame_layout = QVBoxLayout(frame)
        camera_label = QLabel(f"{title}\n(Nonaktif)")
        camera_label.setAlignment(Qt.AlignCenter)
        camera_label.setObjectName("menu-box")
        camera_label.setScaledContents(True)
        frame_layout.addWidget(camera_label)
        button = QPushButton("Aktifkan")
        button.setCheckable(True)
        button.toggled.connect(lambda checked: self.toggle_camera(index, checked))
        frame_layout.addWidget(button)
        self.camera_grid_layout.addWidget(frame)
        self.labels[index] = camera_label
        self.buttons[index] = button

    def toggle_camera(self, index, is_checked):
        # ... (fungsi ini tidak berubah)
        if is_checked:
            self.buttons[index].setText("Nonaktifkan")
            self.labels[index].setText("Menghubungkan...")
            self.threads[index] = QThread()
            self.workers[index] = CameraWorker(camera_index=index)
            self.workers[index].moveToThread(self.threads[index])
            self.threads[index].started.connect(self.workers[index].run)
            self.workers[index].frame_ready.connect(self.update_frame)
            self.workers[index].camera_error.connect(self.handle_camera_error)
            self.threads[index].start()
        else:
            if index in self.workers:
                self.workers[index].stop()
                self.threads[index].quit()
                self.threads[index].wait()
                self.buttons[index].setText("Aktifkan")
                self.labels[index].setText(f"Kamera {index + 1}\n(Nonaktif)")
                self.labels[index].setPixmap(QPixmap())

    def update_frame(self, index, image):
        # ... (fungsi ini tidak berubah)
        if index in self.labels:
            pixmap = QPixmap.fromImage(image)
            self.labels[index].setPixmap(pixmap)

    def handle_camera_error(self, index, message):
        # ... (fungsi ini tidak berubah)
        if index in self.buttons:
            self.buttons[index].setChecked(False)
            self.labels[index].setText(f"Kamera {index + 1}\nError: {message}")
        self.toggle_camera(index, False)

    # --- FUNGSI BARU YANG HILANG ---
    def cleanup(self):
        """Fungsi baru untuk memastikan semua thread kamera berhenti dengan aman."""
        print("Membersihkan thread kamera...")
        for index in self.workers:
            if index in self.threads and self.threads[index].isRunning():
                self.workers[index].stop()
                self.threads[index].quit()
                self.threads[index].wait() # Tunggu hingga thread benar-benar berhenti