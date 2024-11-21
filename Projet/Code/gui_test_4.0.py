import sys
import math
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QComboBox, QPushButton, QVBoxLayout, QWidget, QMessageBox, QDialog, QLabel, QHBoxLayout, QDockWidget
)
from PyQt5.QtGui import QPen, QBrush, QColor, QImage, QPixmap, QPainter
from PyQt5.QtCore import Qt, QTimer


class SerialPortSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Serial Port")
        self.setGeometry(300, 300, 400, 100)

        layout = QVBoxLayout()
        label = QLabel("Select a Serial Port:")
        layout.addWidget(label)

        self.port_combo = QComboBox()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)
        layout.addWidget(self.port_combo)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_selected_port(self):
        return self.port_combo.currentText()


class RadarSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radar Simulator")
        self.setGeometry(100, 100, 1920, 1024)

        # Configurações do radar
        self.SIDE_LENGTH = 1000
        self.MAX_DISTANCE = 1000
        self.echoes = [0] * 80
        self.points_by_angle = {}
        self.acquisition_active = False
        self.captured_pixmap = None

        # Configuração gráfica
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)
        self.scene.setBackgroundBrush(Qt.black)

        # Central do radar
        self.centerX = self.width() // 2
        self.centerY = self.height()
        self.radius = self.SIDE_LENGTH // 2

        # Conexão serial
        self.serial_port = None
        self.setup_serial_connection()

        # Botão para iniciar aquisição
        self.initUI()

        # Timer para verificar dados
        self.timer = QTimer()
        self.timer.timeout.connect(self.checkSerialData)

    def initUI(self):
        start_button = QPushButton("Start Acquisition", self)
        start_button.clicked.connect(self.startAcquisition)
        start_button.setGeometry(10, 10, 150, 40)
        self.start_button = start_button

    def setup_serial_connection(self):
        selector = SerialPortSelector(self)
        if selector.exec_() == QDialog.Accepted:
            port_name = selector.get_selected_port()
            try:
                self.serial_port = serial.Serial(port_name, baudrate=115200, timeout=1)
                QMessageBox.information(self, "Success", f"Connected to {port_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to connect to {port_name}: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No port selected. Running in simulation mode.")

    def startAcquisition(self):
        if self.acquisition_active:
            QMessageBox.warning(self, "Warning", "Acquisition already in progress.")
            return

        self.acquisition_active = True
        self.timer.start(50)  # Iniciar leitura a cada 50ms
        self.scene.clear()  # Limpar a cena anterior

    def checkSerialData(self):
        if not self.acquisition_active or not self.serial_port or not self.serial_port.is_open:
            return

        try:
            line = self.serial_port.readline().decode('utf-8').strip()
            if not line:
                return  # Ignorar linhas vazias

            data = line.split(',')
            if len(data) != 81:
                print(f"Incomplete data received: {line}")
                return  # Ignorar dados incompletos

            # Processar os dados
            angle = int(data[0])  # Primeiro valor é o ângulo
            echoes = [int(value) if value.isdigit() else 0 for value in data[1:]]  # Ecos

            # Atualizar o radar
            self.updateRadar(angle, echoes)

            # Capturar a cena ao atingir o ângulo -80
            if angle == 29:
                print("Acquisition complete: Angle -80 reached.")
                self.captureScene()
                self.timer.stop()
                self.acquisition_active = False  # Parar aquisição

        except ValueError as e:
            print(f"Error parsing data: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def updateRadar(self, angle, echoes):
        if angle not in self.points_by_angle:
            self.points_by_angle[angle] = []

        points = self.points_by_angle[angle]

        # Redesenhar os pontos para o ângulo atual
        for n, distance in enumerate(echoes):
            if n == 0 or distance <= 0:
                continue

            # Escala de distância
            scaled_distance = n * 12.5
            radian = math.radians(angle)
            x = scaled_distance * math.sin(radian)
            y = scaled_distance * math.cos(radian)

            px = self.centerX + x
            py = self.centerY - y

            # Ajustar a cor com base na intensidade
            intensity = min(max(distance, 0), 255)
            color = QColor(intensity, intensity, intensity)  # Preto a branco

            # Criar o ponto
            ellipse = QGraphicsEllipseItem(px - 4, py - 4, 8, 8)
            ellipse.setBrush(QBrush(color))
            ellipse.setPen(QPen(Qt.NoPen))
            self.scene.addItem(ellipse)

            points.append(ellipse)

    def captureScene(self):
        # Captura a cena como imagem
        rect = self.scene.sceneRect()
        image = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
        image.fill(Qt.black)

        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()

        # Salvar a imagem capturada
        self.captured_pixmap = QPixmap.fromImage(image)  # Armazenar para reutilização

        # Substituir o conteúdo do GraphicsView com a imagem capturada
        self.scene.clear()
        self.scene.addPixmap(self.captured_pixmap)

        # Exibir mensagem de confirmação
        QMessageBox.information(self, "Capture Complete", "Image captured and displayed.")

        # Restaurar a interface (manter ferramentas e funcionalidade)
        self.restoreInterface()

    def restoreInterface(self):
        # Certifique-se de que a imagem capturada está sendo exibida
        if hasattr(self, 'captured_pixmap') and self.captured_pixmap:
            self.scene.clear()
            self.scene.addPixmap(self.captured_pixmap)

        # Redesenhar ferramentas e manter a funcionalidade ativa
        self.restoreTools()

        QMessageBox.information(self, "Interface Restored", "Analysis tools and radar data are now active.")

    def restoreTools(self):
        # Certifique-se de que a aba de ferramentas está visível
        if hasattr(self, 'sidebar') and self.sidebar:
            self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar)
        else:
            # Reconstrua a aba de ferramentas caso necessário
            self.sidebar = QDockWidget("Tools", self)
            self.sidebar.setAllowedAreas(Qt.RightDockWidgetArea)

            sidebar_widget = QWidget()
            sidebar_layout = QVBoxLayout()

            # Adiciona os botões novamente
            add_text_btn = QPushButton("Add Text")
            add_text_btn.clicked.connect(self.addTextTool)
            sidebar_layout.addWidget(add_text_btn)

            measure_distance_btn = QPushButton("Measure Distance")
            measure_distance_btn.clicked.connect(self.measureDistanceTool)
            sidebar_layout.addWidget(measure_distance_btn)

            select_objects_btn = QPushButton("Select Objects")
            select_objects_btn.clicked.connect(self.selectObjectsTool)
            sidebar_layout.addWidget(select_objects_btn)

            delete_selected_btn = QPushButton("Delete Selected")
            delete_selected_btn.clicked.connect(self.deleteSelectedTool)
            sidebar_layout.addWidget(delete_selected_btn)

            sidebar_widget.setLayout(sidebar_layout)
            self.sidebar.setWidget(sidebar_widget)
            self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar)

    def addTextTool(self):
        self.scene.mousePressEvent = self.addTextMousePressEvent
        QMessageBox.information(self, "Add Text", "Click on the image to add a text box.")

    def addTextMousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Adiciona uma caixa de texto na posição do clique
            text_box = QGraphicsTextItem("New Text")
            text_box.setPos(event.scenePos())
            text_box.setDefaultTextColor(Qt.white)
            self.scene.addItem(text_box)
        self.scene.mousePressEvent = None  # Desabilitar o evento

    def measureDistanceTool(self):
        self.distance_points = []
        self.scene.mousePressEvent = self.measureDistanceMousePressEvent
        QMessageBox.information(self, "Measure Distance", "Click on two points to measure the distance.")

    def measureDistanceMousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.distance_points.append(event.scenePos())
            if len(self.distance_points) == 2:
                # Desenha a linha de medição
                p1, p2 = self.distance_points
                line = QGraphicsLineItem(p1.x(), p1.y(), p2.x(), p2.y())
                pen = QPen(Qt.red, 2)
                line.setPen(pen)
                self.scene.addItem(line)

                # Calcula a distância e exibe
                distance = math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)
                QMessageBox.information(self, "Distance Measured", f"The distance is: {distance:.2f} pixels.")

                # Limpa os pontos para a próxima medição
                self.distance_points = []

        self.scene.mousePressEvent = None  # Desabilitar o evento


    def selectObjectsTool(self):
        self.selection_mode = True
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.view)
        self.origin = None
        self.scene.mousePressEvent = self.startSelection
        self.scene.mouseMoveEvent = self.updateSelection
        self.scene.mouseReleaseEvent = self.endSelection
        QMessageBox.information(self, "Select Objects", "Click and drag to select objects.")

    def startSelection(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.scenePos()
            self.rubber_band.setGeometry(QRect(self.origin.toPoint(), QSize()))
            self.rubber_band.show()

    def updateSelection(self, event):
        if self.origin:
            rect = QRect(self.origin.toPoint(), event.scenePos().toPoint()).normalized()
            self.rubber_band.setGeometry(rect)

    def endSelection(self, event):
        if self.origin:
            self.rubber_band.hide()
            selection_rect = self.rubber_band.geometry()
            self.selected_objects = []

            # Identificar objetos dentro da área de seleção
            for item in self.scene.items():
                if isinstance(item, (QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem)):
                    if selection_rect.contains(self.view.mapFromScene(item.sceneBoundingRect().toRect()).center()):
                        self.selected_objects.append(item)

            QMessageBox.information(
                self, "Selection Complete", f"{len(self.selected_objects)} objects selected."
            )
        self.scene.mousePressEvent = None
        self.scene.mouseMoveEvent = None
        self.scene.mouseReleaseEvent = None
        self.selection_mode = False


    def deleteSelectedTool(self):
        if not hasattr(self, 'selected_objects') or not self.selected_objects:
            QMessageBox.warning(self, "No Selection", "No objects selected.")
            return

        confirmation = QMessageBox.question(
            self, "Confirm Deletion", f"Are you sure you want to delete {len(self.selected_objects)} selected objects?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            for obj in self.selected_objects:
                self.scene.removeItem(obj)

            QMessageBox.information(self, "Deletion Complete", "Selected objects have been deleted.")
            self.selected_objects = []


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    radar = RadarSimulator()
    radar.show()
    sys.exit(app.exec_())
