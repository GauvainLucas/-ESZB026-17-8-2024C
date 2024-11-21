import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import Qt

class Desenho(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Desenho')

        # Adicionar itens à cena
        self.scene.addEllipse(10, 10, 100, 100, QPen(Qt.black, 2), QBrush(Qt.gray))
        self.scene.addLine(10, 10, 100, 100, QPen(Qt.black, 2))

        # Mostrar a view
        self.show()

    def mousePressEvent(self, event):
        # Selecionar item
        items = self.items(event.pos())
        if items:
            for item in items:
                item.setSelected(True)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        # Excluir item selecionado
        if event.key() == Qt.Key_Delete:
            items = self.scene.selectedItems()
            for item in items:
                self.scene.removeItem(item)
        super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    ex = Desenho()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
