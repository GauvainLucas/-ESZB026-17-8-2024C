#!/usr/bin/python3

# script baseado no codigo disponibilizado em:
# Derek Molloy, Exploring Raspberry Pi: Interfacing to the Real World with Embedded Linux,
# Wiley 2016, ISBN 978-1-119-1868-1, http://www.exploringrpi.com/

import sys
from time import sleep
LED_PATH_amarelo = "/sys/class/gpio/gpio16/"
SYSFS_DIR = "/sys/class/gpio/"
LED_NUMBER_amarelo = "16"

LED_PATH_red = "/sys/class/gpio/gpio20/"
LED_NUMBER_red = "20"

LED_PATH_verde = "/sys/class/gpio/gpio21/"
LED_NUMBER_verde = "21"

def writeLED ( filename, value, path ):
	"Esta funcao escreve o valor 'value' no arquivo 'path+filename'"
	fo = open( path + filename,"w")
	fo.write(value)
	fo.close()
	return


#print("Iniciando o script Python para alterar a gpio " + LED_NUMBER + ".")
if len(sys.argv)!=2:
	print("Numero incorreto de argumentos")
	print(" uso: ./LED.py comando")
	print(" onde comando pode ser: setup, on, off, status, ou close")
	sys.exit(2)

if sys.argv[1]=="on":
	print("Acendendo o LED")
	writeLED (filename="value", value="1")
elif sys.argv[1]=="off":
	print("Desligando o LED")
	writeLED (filename="value", value="0")
elif sys.argv[1]=="setup":
	print("Habilitando a gpio")
	writeLED (filename="export", value=LED_NUMBER_amarelo, path=SYSFS_DIR)
        writeLED (filename="export", value=LED_NUMBER_red, path=SYSFS_DIR)
        writeLED (filename="export", value=LED_NUMBER_verde, path=SYSFS_DIR)
	sleep(0.1)
	writeLED (filename="direction", value="out",path = LED_PATH_amarelo)
        writeLED (filename="direction", value="out",path = LED_PATH_red)
        writeLED (filename="direction", value="out",path = LED_PATH_verde)
elif sys.argv[1]=="close":
	print("Desabilitando a gpio")
	writeLED (filename="unexport", value=LED_NUMBER_amarelo, path=SYSFS_DIR)
	writeLED (filename="unexport", value=LED_NUMBER_red, path=SYSFS_DIR)
	writeLED (filename="unexport", value=LED_NUMBER_verde, path=SYSFS_DIR)
elif sys.argv[1]=="status":
	print("Pegando o status da gpio")
	fo = open( LED_PATH + "value", "r")
	print(fo.read())
	fo.close()
else:
	print("Comando invalido!")

print("Fim do script Python.")


cpt =0
while (cpt < 5):
    writeLED (filename="value", value="1", path=LED_PATH_red)
    sleep(2)
    writeLED (filename="value", value="0", path=LED_PATH_red)
    writeLED (filename="value", value="1", path=LED_PATH_verde)
    sleep(1)
    writeLED (filename="value", value="0", path=LED_PATH_verde)
    writeLED (filename="value", value="1", path=LED_PATH_amarelo)
    sleep(1)
    writeLED (filename="value", value="0", path=LED_PATH_amarelo)
    cpt += 1
