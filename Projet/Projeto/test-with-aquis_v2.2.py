import os
import subprocess
import pygetwindow as gw
import time
#import serial
from PIL import ImageGrab
#from serial import Serial, SerialException

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QPushButton, QFileDialog, QDockWidget, QVBoxLayout, QWidget, QMessageBox, QGraphicsTextItem,
    QGraphicsLineItem, QColorDialog, QFontDialog
)
from PyQt5.QtGui import QPixmap, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

class ImageAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Analyzer with Processing Integration")
        self.setGeometry(100, 100, 800, 600)

        # Initialize Graphics Scene
        self.scene = QGraphicsScene(self)
        self.image_item = None

        # Toolbar and Sidebar
        self.init_toolbar()

    def init_toolbar(self):
        # Button to acquire image from Processing
        acquire_image_btn = QPushButton("Acquire Image", self)
        acquire_image_btn.clicked.connect(self.acquire_image_from_processing)
        self.addToolBar("Main").addWidget(acquire_image_btn)

    def acquire_image_from_processing(self):
        processing_sketch_path = "ultrasonogram_viewer"
        if not os.path.exists(processing_sketch_path):
            QMessageBox.critical(self, "Error", f"Sketch not found: {processing_sketch_path}")
            return

        try:
            print("Running Processing sketch...")
            process = subprocess.Popen(
                [r"C:\Users\Lucas\Downloads\processing-4.3-20241114T003936Z-001\processing-4.3\processing-java", "--sketch=" + processing_sketch_path, "--run"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Start a separate thread to monitor stdout without blocking the main thread
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"Processing Output: {output.strip()}")  # Debug print

                if "END" in output.strip():
                    print("Signal received from Processing! Finalizing acquisition.")
                    break

            process.stdout.close()
            process.wait()  # Aguarda o encerramento do sketch
            
            # Adding a small delay to ensure the Processing window is closed
            time.sleep(5)
            
            # After the acquisition is finished, capture the screen
            window_title = "ultrasonogram_viewer"  # Adjust this title as needed
            window = self.wait_for_processing_window(window_title)
            if window:
                screenshot_path = "processing_screenshot.png"
                if self.capture_processing_window(window, screenshot_path):
                    self.load_image(screenshot_path)
                else:
                    QMessageBox.critical(self, "Error", "Failed to capture the Processing window.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred.\n\n{e}")

    def wait_for_processing_window(self, window_title, max_retries=20, retry_interval=0.5):
        for _ in range(max_retries):
            windows = gw.getWindowsWithTitle(window_title)
            if windows and windows[0].isVisible():
                print(f"Processing window '{window_title}' is fully loaded.")
                return windows[0]
            time.sleep(retry_interval)
        QMessageBox.warning(self, "Error", f"Window with title '{window_title}' not loaded.")
        return None

    def capture_processing_window(self, window, output_file):
        bbox = (window.left, window.top, window.right, window.bottom)
        screenshot = ImageGrab.grab(bbox)
        screenshot.save(output_file)
        print(f"Screenshot saved to {output_file}")
        return True

    def load_image(self, file_path):
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            if self.image_item:
                self.scene.removeItem(self.image_item)
            self.image_item = self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(QRectF(pixmap.rect()))
            print("Image successfully added to the scene.")
        else:
            print("Failed to load image.")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ImageAnalyzer()
    window.show()
    sys.exit(app.exec_())
