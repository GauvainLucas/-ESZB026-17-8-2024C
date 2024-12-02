import sys
import os
import subprocess
import pyautogui
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QPushButton, QFileDialog, QDockWidget, QVBoxLayout, QWidget, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPen, QPainter
from PyQt5.QtCore import Qt, QPointF, QRectF


class DataAcquisitionAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Acquisition Analyzer")
        self.setGeometry(100, 100, 800, 600)

        # Initialize Graphics View and Scene
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        # Toolbar and Sidebar
        self.init_toolbar()
        self.init_sidebar()

        # State Variables
        self.image_item = None

    def init_toolbar(self):
        acquire_data_btn = QPushButton("Acquire Data", self)
        acquire_data_btn.clicked.connect(self.acquire_data)
        self.addToolBar("Main").addWidget(acquire_data_btn)

    def init_sidebar(self):
        self.sidebar = QDockWidget("Tools", self)
        self.sidebar.setAllowedAreas(Qt.RightDockWidgetArea)

        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()

        # Delete Selected Button
        delete_selected_btn = QPushButton("Delete Selected")
        delete_selected_btn.clicked.connect(self.delete_selected_items)
        sidebar_layout.addWidget(delete_selected_btn)

        sidebar_widget.setLayout(sidebar_layout)
        self.sidebar.setWidget(sidebar_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar)

    def acquire_data(self):
        # Path to the Processing sketch
        processing_sketch_path = r"C:\Users\jjvin\Desktop\Projeto\ultrasonogram_viewer"
        if not processing_sketch_path:
            QMessageBox.warning(self, "No Folder Selected", "Please select the folder containing the Processing sketch.")
            return

        try:
            # Run the Processing sketch
            processing_java_path = r"C:\Processing\processing-java"  # Substitua pelo caminho exato no seu sistema
            subprocess.Popen([processing_java_path, "--sketch=" + processing_sketch_path, "--run"])

            QMessageBox.information(self, "Acquisition Started", "Processing sketch is running. Please wait.")

            # Wait for the acquisition to finish
            time.sleep(15)  # Adjust the time as needed to match the Processing sketch runtime

            # Capture the screen
            screenshot_path = os.path.join(processing_sketch_path, "output.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)

            # Add the captured image to the scene
            self.add_image_to_scene(screenshot_path)

            QMessageBox.information(self, "Acquisition Completed", f"Data acquisition completed. Screenshot saved to: {screenshot_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def add_image_to_scene(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            if self.image_item:
                self.scene.removeItem(self.image_item)
            self.image_item = self.scene.addPixmap(pixmap)
            self.image_item.setZValue(-1)  # Ensure image is behind all other items
            self.scene.setSceneRect(QRectF(pixmap.rect()))  # Convert QRect to QRectF

    def delete_selected_items(self):
        selected_items = self.scene.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "No items selected.")
            return

        confirmation = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete the selected items?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            for item in selected_items:
                self.scene.removeItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataAcquisitionAnalyzer()
    window.show()
    sys.exit(app.exec_())
