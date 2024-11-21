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
        self.MAX_DISTANCE = 1000
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

        # Timer para verificar dados
        self.timer = QTimer()
        self.timer.timeout.connect(self.checkSerialData)
        self.timer.start(10)  # Verifica novos dados a cada 10ms

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

    def checkSerialData(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                # Limpar linhas antigas no buffer serial
                while self.serial_port.in_waiting > 1:
                    self.serial_port.readline()  # Descarte linhas antigas

                # Ler a última linha disponível
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    radar = RadarSimulator()
    radar.show()
    sys.exit(app.exec_())
