import sys
import math
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QComboBox, QPushButton, QVBoxLayout, QWidget, QMessageBox, QDialog, QLabel, QHBoxLayout
)
from PyQt5.QtGui import QPen, QBrush, QColor
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
        self.ANGLE_BOUNDS = 80
        self.ANGLE_STEP = 2
        self.MAX_DISTANCE = 1000
        self.angle = 0
        self.echoes = [0] * 80
        self.points_by_angle = {}

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

        # Timer para atualização
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateRadar)
        self.timer.start(50)  # Atualiza a cada 50ms

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

    def read_serial_data(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()

                if not line:
                    print("Empty line received, treating as no data.")
                    return  # Ignorar se a linha estiver completamente vazia

                data = line.split(',')
                if len(data) < 81:
                    print(f"Incomplete data received: {line}, filling with zeros.")
                    # Completar com zeros para ter 80 valores
                    data += ['0'] * (81 - len(data))

                # Processar os dados
                self.angle = int(data[0])  # Primeiro valor é o ângulo
                self.echoes = [
                    int(value) if value.isdigit() else 0 for value in data[1:]
                ]  # Substituir valores inválidos por 0

            except ValueError as e:
                print(f"Error parsing data: {e}, line: {line}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    def drawRadar(self):
        pen = QPen(Qt.gray)
        for i in range(0, self.SIDE_LENGTH // 100 + 1):
            radius = 100 * i
            self.scene.addEllipse(self.centerX - radius, self.centerY - radius, 2 * radius, 2 * radius, pen)

        for i in range(0, self.ANGLE_BOUNDS * 2 // 20 + 1):
            angle = -self.ANGLE_BOUNDS + i * 20
            rad_angle = math.radians(angle)
            x = self.centerX + self.radius * math.sin(rad_angle)
            y = self.centerY - self.radius * math.cos(rad_angle)
            self.scene.addLine(self.centerX, self.centerY, x, y, pen)

    def drawObjects(self):
        if self.angle not in self.points_by_angle:
            self.points_by_angle[self.angle] = []

        points = self.points_by_angle[self.angle]

        for n, distance in enumerate(self.echoes):
            if n == 0 or distance <= 0:
                continue

            # Escala de distância igual ao Processing
            scaled_distance = n * 12.5
            radian = math.radians(self.angle)
            x = scaled_distance * math.sin(radian)
            y = scaled_distance * math.cos(radian)

            px = self.centerX + x
            py = self.centerY - y

            # Ajustar a cor com base na intensidade (escala de cinza)
            intensity = min(max(distance, 0), 255)  # Garantir valores entre 0 e 255
            color = QColor(intensity, intensity, intensity)  # Matiz de preto a branco

            # Debugging: imprimir os valores calculados
            print(f"Angle: {self.angle}, Scaled Distance: {scaled_distance}, Point: ({px}, {py}), Intensity: {intensity}")

            # Criar o ponto no radar
            ellipse = QGraphicsEllipseItem(px - 4, py - 4, 8, 8)
            ellipse.setBrush(QBrush(color))
            ellipse.setPen(QPen(Qt.NoPen))
            self.scene.addItem(ellipse)

            points.append(ellipse)

    def updateRadar(self):
        self.read_serial_data()
        self.drawRadar()
        self.drawObjects()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    radar = RadarSimulator()
    radar.show()
    sys.exit(app.exec_())
