import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem,
    QGraphicsLineItem, QFileDialog, QDockWidget, QVBoxLayout, QWidget, QPushButton, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPen, QPainter
from PyQt5.QtCore import Qt, QPointF, QRectF


class ImageAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Analyzer with QGraphicsView")
        self.setGeometry(100, 100, 800, 600)

        # Initialize Graphics View and Scene
        self.view = CustomGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        # Toolbar and Sidebar
        self.init_toolbar()
        self.init_sidebar()

        # State Variables
        self.image_item = None
        self.adding_text = False
        self.measuring_distance = False
        self.first_point = None

    def init_toolbar(self):
        open_image_btn = QPushButton("Open Image", self)
        open_image_btn.clicked.connect(self.open_image)
        self.addToolBar("Main").addWidget(open_image_btn)

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

        sidebar_widget.setLayout(sidebar_layout)
        self.sidebar.setWidget(sidebar_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            pixmap = QPixmap(file_name)
            if not pixmap.isNull():
                if self.image_item:
                    self.scene.removeItem(self.image_item)
                self.image_item = self.scene.addPixmap(pixmap)
                self.image_item.setZValue(-1)  # Ensure image is behind all other items
                self.scene.setSceneRect(QRectF(pixmap.rect()))  # Convert QRect to QRectF
                print("Image successfully added to the scene.")
            else:
                print("Failed to load image.")

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
            line.setPen(QPen(Qt.red, 2))
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


class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHints(self.renderHints() | QPainter.Antialiasing)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 0.85
        self.scale(factor, factor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageAnalyzer()
    window.show()
    sys.exit(app.exec_())
