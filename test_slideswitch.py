#!/usr/bin/env python3
"""
Simple test script to verify SlideSwitch functionality
"""
import sys
try:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    from PyQt5.QtCore import Qt
    from slide_switch import SlideSwitch
    
    class TestWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("SlideSwitch Test")
            self.setGeometry(100, 100, 400, 300)
            
            layout = QVBoxLayout()
            
            # Title
            title = QLabel("SlideSwitch Component Test")
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            
            # Test switches
            switch1 = SlideSwitch()
            switch1.setChecked(True)
            switch1.toggled.connect(lambda checked: print(f"Switch 1: {'ON' if checked else 'OFF'}"))
            layout.addWidget(switch1)
            
            switch2 = SlideSwitch()
            switch2.setChecked(False)
            switch2.toggled.connect(lambda checked: print(f"Switch 2: {'ON' if checked else 'OFF'}"))
            layout.addWidget(switch2)
            
            switch3 = SlideSwitch()
            switch3.setChecked(True)
            switch3.toggled.connect(lambda checked: print(f"Switch 3: {'ON' if checked else 'OFF'}"))
            layout.addWidget(switch3)
            
            self.setLayout(layout)
    
    def main():
        app = QApplication(sys.argv)
        window = TestWindow()
        window.show()
        sys.exit(app.exec_())
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Import error: {e}")
    print("PyQt5 may not be properly installed.")
    sys.exit(1)
