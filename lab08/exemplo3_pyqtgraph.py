#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import numpy as np
import serial
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import atexit

# Initialisation de la connexion série
conexaoSerial = serial.Serial('/dev/ttyACM0', 115200)

# Variables globales
npontos = 800
x_atual = 0
data1 = np.zeros(npontos)
previousTime = time.time() * 1000  # Temps initial en millisecondes

# Fonctions
def inicia_coleta():
    conexaoSerial.write(b'i')

def para_coleta():
    conexaoSerial.write(b'p')

def ajusta_intervalo(delta):
    global intervalo_atual
    intervalo_atual = max(10, intervalo_atual + delta)  # Minimum 10 ms
    conexaoSerial.write(b't')
    conexaoSerial.write(bytes([intervalo_atual & 0xFF, (intervalo_atual >> 8) & 0xFF]))
    label_intervalo.setText(f"Intervalo: {intervalo_atual} ms")

def demande_intervalo():
    conexaoSerial.write(b'v')  # Commande pour demander l'intervalle
    if conexaoSerial.inWaiting() >= 2:
        low_byte = conexaoSerial.read()
        high_byte = conexaoSerial.read()
        intervalo = (ord(high_byte) << 8) | ord(low_byte)
        label_intervalo.setText(f"Intervalo: {intervalo} ms")

def update():
    global data1, x_atual, previousTime
    if conexaoSerial.inWaiting() > 1:
        dado1 = conexaoSerial.read()
        dado2 = conexaoSerial.read()
        novodado = float((ord(dado1) + ord(dado2) * 256.0) * 5.0 / 1023.0)
        data1[x_atual] = novodado
        data1[(x_atual + 1) % npontos] = np.nan
        x_atual = (x_atual + 1) % npontos
        curve1.setData(data1, connect="finite")
        actualTime = time.time() * 1000
        taxa = str(round(actualTime - previousTime))
        previousTime = actualTime
        texto.setText(f"Fréquence: {taxa.zfill(3)} ms")

def saindo():
    conexaoSerial.write(b'p')
    print('Arrêt de la connexion série')

# Initialisation graphique
app = QtGui.QApplication([])
win = pg.GraphicsWindow()
win.setWindowTitle('Collecte de données via Arduino')
p1 = win.addPlot()
p1.setYRange(0, 5, padding=0)
curve1 = p1.plot(data1)
texto = pg.TextItem(text="", color=(255, 255, 0), anchor=(0, 1))
p1.addItem(texto)
texto.setPos(0, 0)

# Ajouter des boutons
layout = win.addLayout(row=1, col=0)
proxy_inicia = QtGui.QGraphicsProxyWidget()
btn_inicia = QtGui.QPushButton('Démarrer')
btn_inicia.clicked.connect(inicia_coleta)
proxy_inicia.setWidget(btn_inicia)
layout.addItem(proxy_inicia, row=0, col=0)

proxy_para = QtGui.QGraphicsProxyWidget()
btn_para = QtGui.QPushButton('Arrêter')
btn_para.clicked.connect(para_coleta)
proxy_para.setWidget(btn_para)
layout.addItem(proxy_para, row=1, col=0)

proxy_augment = QtGui.QGraphicsProxyWidget()
btn_augment = QtGui.QPushButton('Augmenter intervalle')
btn_augment.clicked.connect(lambda: ajusta_intervalo(10))
proxy_augment.setWidget(btn_augment)
layout.addItem(proxy_augment, row=2, col=0)

proxy_diminue = QtGui.QGraphicsProxyWidget()
btn_diminue = QtGui.QPushButton('Diminuer intervalle')
btn_diminue.clicked.connect(lambda: ajusta_intervalo(-10))
proxy_diminue.setWidget(btn_diminue)
layout.addItem(proxy_diminue, row=3, col=0)

proxy_demande = QtGui.QGraphicsProxyWidget()
btn_demande = QtGui.QPushButton('Demander intervalle')
btn_demande.clicked.connect(demande_intervalo)
proxy_demande.setWidget(btn_demande)
layout.addItem(proxy_demande, row=4, col=0)

label_intervalo = QtGui.QLabel("Intervalle: 100 ms")
layout.addItem(QtGui.QGraphicsProxyWidget().setWidget(label_intervalo), row=5, col=0)

# Démarrer le timer
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)

# Gestion des sorties
atexit.register(saindo)

# Exécution
if __name__ == '__main__':
    QtGui.QApplication.instance().exec_()

