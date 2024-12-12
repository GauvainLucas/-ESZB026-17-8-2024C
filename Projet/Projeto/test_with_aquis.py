import os
# import pygetwindow as gw #for windows
import pyautogui as gui #for linux
import time
import subprocess
from PIL import ImageGrab
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QPushButton, QFileDialog, QDockWidget, QVBoxLayout, QWidget, QMessageBox, QGraphicsTextItem,
    QGraphicsLineItem, QColorDialog, QFontDialog, QMessageBox, QShortcut, QLineEdit, QInputDialog
)
from PyQt5.QtGui import QPixmap, QPen, QColor, QFont, QImage, QPainter
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QKeySequence

class Data:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def to_dict(self):
        return {"name": self.name, "value": self.value}
    
def get_windows_with_title(title):
        # Exécuter wmctrl pour lister toutes les fenêtres
        result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
        
        # Filtrer les fenêtres qui correspondent au titre (insensible à la casse)
        windows = []
        for line in result.stdout.splitlines():
            if title.lower() in line.lower():
                windows.append(line)
        
        return windows

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

         # Undo/Redo Stacks
        self.undo_stack = []
        self.redo_stack = []

        # data dict
        self.dict = {}
        self.dict_index = 0
        
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

        # Add change text color
        change_text_color_btn = QPushButton("Change Text Color")
        change_text_color_btn.clicked.connect(self.change_text_color)
        sidebar_layout.addWidget(change_text_color_btn)

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

        # change text button
        change_font_btn = QPushButton("Change Text Font")
        change_font_btn.clicked.connect(self.change_text_font)
        sidebar_layout.addWidget(change_font_btn)

        # Save image button
        save_image_btn = QPushButton("Save image")
        save_image_btn.clicked.connect(self.save_image)
        sidebar_layout.addWidget(save_image_btn)

        # Generate HTML report button
        generate_html = QPushButton("Generate report")
        generate_html.clicked.connect(self.generate_report)
        sidebar_layout.addWidget(generate_html)

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
            self.save_scene_as_image("temp/before.png")
            print("Image successfully added to the scene.")
        else:
            print("Failed to load image.")

    def capture_processing_window(self, window_title, output_file):
        """
        Captures a screenshot of the specified window by title.
        """
        # Locate the window by title
        # windows = gw.getWindowsWithTitle(window_title)
        windows = get_windows_with_title(window_title)
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
        processing_sketch_path = r"ultrasonogram_viewer\ultrasonogram_viewer.pde"

        # Check if the sketch exists
        if not os.path.exists(processing_sketch_path):
            QMessageBox.critical(self, "Error", f"Sketch not found: {processing_sketch_path}")
            return

        # Run the Processing sketch
        try:
            print("Running Processing sketch...")
            subprocess.Popen([r"processing-4.3\processing-java", "--sketch=" + os.path.dirname(processing_sketch_path), "--run"])

            QMessageBox.information(self, "Acquisition Started", "Processing sketch is running. Please wait.")

            # Wait for the Processing window to appear
            window_title = "ultrasonogram_viewer"  # Modify this to match the window title
            max_retries = 20  # Retry up to 20 times (total ~10 seconds)
            retry_interval = 3  # Time to wait between retries (0.5 seconds)


            for _ in range(max_retries):
                # windows = gw.getWindowsWithTitle(window_title)
                windows = get_windows_with_title(window_title)
                if windows:
                    print("Processing window found.")
                    break
                time.sleep(retry_interval)
            else:
                QMessageBox.warning(self, "Error", f"Window with title '{window_title}' not found.")
                return
            # Delay to ensure the window is fully loaded
            time.sleep(10)  # Wait 2 seconds after detecting the window
            # Capture screenshot of the Processing window
            output_file = r"processing_screenshot.png"
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

    def change_text_color(self):
        color = QColorDialog.getColor(self.current_text_color, self, "Select Text Color")
        if color.isValid():
            self.current_text_color = color
            print(f"Text color changed to: {color.name()}")

            # Aplicar a nova cor a todas as caixas de texto existentes
            for item in self.scene.items():
                if isinstance(item, QGraphicsTextItem):
                    item.setDefaultTextColor(self.current_text_color)


    def add_text_item(self, position):
        text_item = QGraphicsTextItem("New Text")
        text_item.setPos(position)
        text_item.setFont(self.current_text_font)
        text_item.setDefaultTextColor(self.current_text_color)
        text_item.setFlag(QGraphicsTextItem.ItemIsMovable)
        text_item.setFlag(QGraphicsTextItem.ItemIsSelectable)
        text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.scene.addItem(text_item)

        # Adiciona ação no undo_stack
        self.undo_stack.append(("add_text", text_item))
        self.redo_stack.clear()  # Limpa o redo_stack ao fazer uma nova ação

    def add_distance_point(self, position):
        if self.first_point is None:
            self.first_point = position
            print(f"First point set at: {position}")
        else:
            line = QGraphicsLineItem(self.first_point.x(), self.first_point.y(), position.x(), position.y())
            pen = QPen(self.current_line_color, 2)
            line.setPen(pen)
            line.setFlag(QGraphicsLineItem.ItemIsSelectable)
            self.scene.addItem(line)

            # Calcula a distância
            distance = ((position.x() - self.first_point.x())**2 + (position.y() - self.first_point.y())**2)**0.5

            # convert in mm regarding the screen

            # Récupération de la résolution de l'écran en DPI
            screen = QApplication.primaryScreen()
            dpi = screen.physicalDotsPerInch()

            # Conversion de pixels en millimètres
            distance = distance / dpi * 25.4
            # convert in mm regarding the screen

            distance_text = QGraphicsTextItem(f"{distance:.2f} mm")
            midpoint = QPointF((self.first_point.x() + position.x()) / 2, (self.first_point.y() + position.y()) / 2)
            distance_text.setPos(midpoint)
            distance_text.setFont(self.current_text_font)
            distance_text.setDefaultTextColor(self.current_line_color)
            distance_text.setFlag(QGraphicsTextItem.ItemIsMovable)
            distance_text.setFlag(QGraphicsTextItem.ItemIsSelectable)
            self.scene.addItem(distance_text)
            # save the distance
            # name it
            text, pressed = QInputDialog.getText(window, "Input Text", "Enter the easurement name:", QLineEdit.Normal, "")
            print(text)
            new_data = Data(text, distance_text.toPlainText())
             # Ajout au dictionnaire avec une clé unique
            self.dict[self.dict_index] = new_data.to_dict()
            self.dict_index += 1

            # Adiciona ações no undo_stack
            self.undo_stack.append(("add_line", line, distance_text))
            self.redo_stack.clear()  # Limpa o redo_stack ao fazer uma nova ação

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

    def delete_selected_items(self):
        selected_items = self.scene.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Delete", "No items selected to delete.")
            return

        confirmation = QMessageBox.question(
            self, "Confirm Deletion", f"Are you sure you want to delete {len(selected_items)} selected item(s)?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            actions = []

            for item in selected_items:
                self.scene.removeItem(item)
                if isinstance(item, QGraphicsTextItem):
                    actions.append(("add_text", item))
                elif isinstance(item, QGraphicsLineItem):
                    distance_text = next(
                        (i for i in self.scene.items() if isinstance(i, QGraphicsTextItem) and i.pos() == item.boundingRect().center()),
                        None
                    )
                    actions.append(("add_line", item, distance_text))
                    if distance_text:
                        self.scene.removeItem(distance_text)

            self.undo_stack.append(("delete", actions))
            self.redo_stack.clear()
            print(f"Deleted {len(selected_items)} item(s).")

    def undo(self):
        if not self.undo_stack:
            QMessageBox.information(self, "Undo", "Nothing to undo.")
            return

        action = self.undo_stack.pop()

        if action[0] == "add_text":
            self.scene.removeItem(action[1])
            self.redo_stack.append(action)

        elif action[0] == "add_line":
            self.scene.removeItem(action[1])
            self.scene.removeItem(action[2])
            self.redo_stack.append(action)

        elif action[0] == "delete":
            for sub_action in action[1]:
                if sub_action[0] == "add_text":
                    self.scene.addItem(sub_action[1])
                elif sub_action[0] == "add_line":
                    self.scene.addItem(sub_action[1])
                    if sub_action[2]:
                        self.scene.addItem(sub_action[2])
            self.redo_stack.append(action)

        print("Undo performed.")

    def redo(self):
        if not self.redo_stack:
            QMessageBox.information(self, "Redo", "Nothing to redo.")
            return

        action = self.redo_stack.pop()

        if action[0] == "add_text":
            self.scene.addItem(action[1])
            self.undo_stack.append(action)

        elif action[0] == "add_line":
            self.scene.addItem(action[1])
            self.scene.addItem(action[2])
            self.undo_stack.append(action)

        elif action[0] == "delete":
            for sub_action in action[1]:
                if sub_action[0] == "add_text":
                    self.scene.removeItem(sub_action[1])
                elif sub_action[0] == "add_line":
                    self.scene.removeItem(sub_action[1])
                    if sub_action[2]:
                        self.scene.removeItem(sub_action[2])
            self.undo_stack.append(action)

        print("Redo performed.")
    
    # Método para salvar a cena como imagem
    def save_scene_as_image(self, file_path):
        rect = self.scene.sceneRect()
        image = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
        image.fill(Qt.white)  # Fundo branco

        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()
        image.save(file_path)
        
        print(f"Scene saved as image: {file_path}")

    # Método para salvar a imagem quando o botão é clicado
    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files (*.png *.jpg)")
        if file_path:
            self.save_scene_as_image(file_path)

    def generate_html_report(self, file_path):
        self.save_scene_as_image("temp/after.png") 
        if not file_path: 
            QMessageBox.warning(self, "Error", "No file selected for saving the report.")
            return

        try:
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        font-family: sans-serif;
                        margin: 20px;
                    }

                    h1, h2 {
                        text-align: center;
                    }

                    ul {
                        list-style-type: none;
                        padding: 0;
                    }

                    li {
                        margin-bottom: 5px;
                    }

                    img {
                        display: block;
                        max-width: 65%;
                        height: auto; 
                        margin-bottom: 10px;
                        margin-left: auto;
                        margin-right: auto;
                    }

                    table {
                    border-collapse: collapse;
                    width: 80%;
                    margin-right: auto;
                    margin-left: auto;
                    }

                    th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                    }

                    th {
                    background-color: #f2f2f2;
                    text-align: center; /* Centre le texte horizontalement */
                    font-weight: bold; /* Met le texte en gras */
                    }
                </style>
            </head>
            <body>
                <h1>Scene Report</h1>
                <img src="temp/before.png" alt="Image Load">
                <hr width="100%" size="2">
                <h2>Measurement Report</h2>
                <table>"""
            # Add data from self.dict (assuming the structure is as described)
            html_content += f"<tr><th>Measurement</th><th>Size</th></tr>"
            for a, distance in self.dict.items():
                html_content += f"<tr><td>{distance['name']}</td><td>{distance['value']}</td></tr>"
            html_content += """</table>
                <hr width="100%" size="2">
                <h2>Rendered Scene</h2>
                <img src="temp/after.png" alt="Image after analyse">
            </body>
            </html>
            """

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(html_content)

            QMessageBox.information(self, "Success", f"HTML report saved successfully: {file_path}")
            print(f"HTML report saved as: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save the report: {str(e)}")
            print(f"Error saving report: {str(e)}")

    # Método para gerar o relatório HTML quando o botão é clicado
    def generate_report(self):
        # just to test
        print(self.dict)
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "HTML Files (*.html)")
        if file_path:  # Proceed only if the user selects a valid path
            self.generate_html_report(file_path)
        else:
            QMessageBox.information(self, "Canceled", "Report generation canceled.")



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ImageAnalyzer()
    window.show()
    sys.exit(app.exec_())
