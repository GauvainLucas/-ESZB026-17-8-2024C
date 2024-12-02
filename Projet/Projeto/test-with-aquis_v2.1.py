import os
import pygetwindow as gw
import time
import subprocess
from PIL import ImageGrab
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QPushButton, QFileDialog, QDockWidget, QVBoxLayout, QWidget, QMessageBox, QGraphicsTextItem,
    QGraphicsLineItem, QColorDialog, QFontDialog
)
from PyQt5.QtGui import QPixmap, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut


void QGraphicsTextItem::setDefaultTextColor ( const QColor & col ) 

class ImageAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Analyzer with Processing Integration")
        self.setGeometry(100, 100, 800, 600)

        # Initialize Graphics View and Scene
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)
        self.image_item = None
        
        # Current Styles
        self.current_line_color = QColor(Qt.white)
        self.current_text_font = QFont("Arial", 12)
        self.current_text_color = QColor(Qt.white)

        # Toolbar and Sidebar
        self.init_toolbar()
        self.init_sidebar()

        # Atalhos de Teclado
        self.init_shortcuts()

    def init_toolbar(self):
        # Button to load images from file
        open_image_btn = QPushButton("Open Image", self)
        open_image_btn.clicked.connect(self.open_image)
        self.addToolBar("Main").addWidget(open_image_btn)

        # Button to acquire image from Processing
        acquire_image_btn = QPushButton("Acquire Image", self)
        acquire_image_btn.clicked.connect(self.acquire_image_from_processing)
        self.addToolBar("Main").addWidget(acquire_image_btn)

    def init_sidebar(self):
        self.sidebar = QDockWidget("Tools", self)
        self.sidebar.setAllowedAreas(Qt.RightDockWidgetArea)

        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()

        # Add Text Button
        add_text_btn = QPushButton("Add Text")
        add_text_btn.clicked.connect(self.activate_add_text)
        sidebar_layout.addWidget(add_text_btn)

        # Measure Distance Button
        measure_distance_btn = QPushButton("Measure Distance")
        measure_distance_btn.clicked.connect(self.activate_measure_distance)
        sidebar_layout.addWidget(measure_distance_btn)

        # Delete Selected Button
        delete_selected_btn = QPushButton("Delete Selected")
        delete_selected_btn.clicked.connect(self.delete_selected_items)
        sidebar_layout.addWidget(delete_selected_btn)

        # Personalization Buttons
        change_color_btn = QPushButton("Change Line Color")
        change_color_btn.clicked.connect(self.change_line_color)
        sidebar_layout.addWidget(change_color_btn)

        change_font_btn = QPushButton("Change Text Font")
        change_font_btn.clicked.connect(self.change_text_font)
        sidebar_layout.addWidget(change_font_btn)

        sidebar_widget.setLayout(sidebar_layout)
        self.sidebar.setWidget(sidebar_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar)

    def init_shortcuts(self):
        # Atalhos para desfazer, refazer e deletar
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.redo)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.delete_selected_items)


    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            self.load_image(file_name)

    def load_image(self, file_path):
        """
        Loads an image file into the QGraphicsScene.
        """
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            if self.image_item:
                self.scene.removeItem(self.image_item)
            self.image_item = self.scene.addPixmap(pixmap)
            self.image_item.setZValue(-1)  # Ensure image is behind all other items
            self.scene.setSceneRect(QRectF(pixmap.rect()))  # Convert QRect to QRectF
            print("Image successfully added to the scene.")
        else:
            print("Failed to load image.")

    def capture_processing_window(self, window_title, output_file):
        """
        Captures a screenshot of the specified window by title.
        """
        # Locate the window by title
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            print(f"No window with title '{window_title}' found.")
            return False

        # Get the first matching window
        window = windows[0]
        print(f"Capturing window: {window.title}")

        # Get the bounding box of the window
        bbox = (window.left, window.top, window.right, window.bottom)

        # Capture the screen within the bounding box
        screenshot = ImageGrab.grab(bbox)
        screenshot.save(output_file)
        print(f"Screenshot saved to {output_file}")

        return True
    
    def acquire_image_from_processing(self):
        # Path to the Processing sketch
        processing_sketch_path = r"C:\Users\jjvin\Desktop\Projeto\ultrasonogram_viewer\ultrasonogram_viewer.pde"

        # Check if the sketch exists
        if not os.path.exists(processing_sketch_path):
            QMessageBox.critical(self, "Error", f"Sketch not found: {processing_sketch_path}")
            return

        # Run the Processing sketch
        try:
            print("Running Processing sketch...")
            subprocess.Popen([r"C:\Processing\processing-java", "--sketch=" + os.path.dirname(processing_sketch_path), "--run"])

            QMessageBox.information(self, "Acquisition Started", "Processing sketch is running. Please wait.")

            # Wait for the Processing window to appear
            window_title = "ultrasonogram_viewer"  # Modify this to match the window title
            max_retries = 20  # Retry up to 20 times (total ~10 seconds)
            retry_interval = 3  # Time to wait between retries (0.5 seconds)


            for _ in range(max_retries):
                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    print("Processing window found.")
                    break
                time.sleep(retry_interval)
            else:
                QMessageBox.warning(self, "Error", f"Window with title '{window_title}' not found.")
                return
            # Delay to ensure the window is fully loaded
            time.sleep(15)  # Wait 2 seconds after detecting the window
            # Capture screenshot of the Processing window
            output_file = r"C:\Users\jjvin\Desktop\Projeto\processing_screenshot.png"
            if self.capture_processing_window(window_title, output_file):
                self.load_image(output_file)
            else:
                QMessageBox.critical(self, "Error", f"Failed to capture the Processing window.")

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to run Processing sketch.\n\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred.\n\n{e}")
    def activate_add_text(self):
        self.adding_text = True
        self.measuring_distance = False

    def activate_measure_distance(self):
        self.measuring_distance = True
        self.adding_text = False
        self.first_point = None  # Ensure no leftover first point

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.view.mapToScene(event.pos())

            if self.adding_text:
                self.add_text_item(scene_pos)
            elif self.measuring_distance:
                self.add_distance_point(scene_pos)

    def add_text_item(self, position):
    
        text_item = QGraphicsTextItem("New Text")
        text_item.setPos(position)
        text_item.setFlag(QGraphicsTextItem.ItemIsMovable)
        text_item.setFlag(QGraphicsTextItem.ItemIsSelectable)
        text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.scene.addItem(text_item)

    def add_distance_point(self, position):
        if self.first_point is None:
            # Set the first point for distance measurement
            self.first_point = position
            print(f"First point set at: {position}")
        else:
            # Draw a line between first_point and position
            line = QGraphicsLineItem(self.first_point.x(), self.first_point.y(), position.x(), position.y())
            line.setPen(QPen(Qt.white, 2))
            line.setFlag(QGraphicsLineItem.ItemIsSelectable)
            self.scene.addItem(line)

            # Calculate the distance
            distance = ((position.x() - self.first_point.x())**2 + (position.y() - self.first_point.y())**2)**0.5
            print(f"Distance measured: {distance:.2f} px")

            # Add text to show the distance
            distance_text = QGraphicsTextItem(f"{distance:.2f} px")
            midpoint = QPointF((self.first_point.x() + position.x()) / 2, (self.first_point.y() + position.y()) / 2)
            distance_text.setPos(midpoint)
            distance_text.setFlag(QGraphicsTextItem.ItemIsMovable)
            distance_text.setFlag(QGraphicsTextItem.ItemIsSelectable)
            self.scene.addItem(distance_text)

            # Reset first_point for the next measurement
            self.first_point = None

    def change_line_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_line_color = color
            print(f"Line color changed to: {color.name()}")

    def change_text_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.current_text_font = font
            print(f"Text font changed to: {font.family()}")

    def undo(self):
        print("Undo not implemented yet.")

    def redo(self):
        print("Redo not implemented yet.")

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
    import sys
    app = QApplication(sys.argv)
    window = ImageAnalyzer()
    window.show()
    sys.exit(app.exec_())
