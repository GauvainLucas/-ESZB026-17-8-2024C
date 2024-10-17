#!/bin/bash

# To execute : 
# 	chmod +x LED.sh
# 	./LED.sh


# GPIO pins for LEDs
LED_PIN_AMARELO=16
LED_PIN_RED=20
LED_PIN_VERDE=21
SYSFS_DIR="/sys/class/gpio"


writeLED() {
    local filename=$1
    local value=$2
    local path=$3
    echo "$value" > "$path/$filename"
}

setup() {
    echo "$LED_PIN_AMARELO" > "$SYSFS_DIR/export"
    echo "$LED_PIN_RED" > "$SYSFS_DIR/export"
    echo "$LED_PIN_VERDE" > "$SYSFS_DIR/export"
    sleep 0.1
    echo "out" > "$SYSFS_DIR/gpio$LED_PIN_AMARELO/direction"
    echo "out" > "$SYSFS_DIR/gpio$LED_PIN_RED/direction"
    echo "out" > "$SYSFS_DIR/gpio$LED_PIN_VERDE/direction"
}

close() {
    echo "$LED_PIN_AMARELO" > "$SYSFS_DIR/unexport"
    echo "$LED_PIN_RED" > "$SYSFS_DIR/unexport"
    echo "$LED_PIN_VERDE" > "$SYSFS_DIR/unexport"
}

# Main program
setup
cpt=0
while [ $cpt -lt 5 ]; do
    # Red 
    echo "1" > "$SYSFS_DIR/gpio$LED_PIN_RED/value"
    sleep 2
    echo "0" > "$SYSFS_DIR/gpio$LED_PIN_RED/value"
    # Green 
    echo "1" > "$SYSFS_DIR/gpio$LED_PIN_VERDE/value"
    sleep 1
    echo "0" > "$SYSFS_DIR/gpio$LED_PIN_VERDE/value"
    # Yellow 
    echo "1" > "$SYSFS_DIR/gpio$LED_PIN_AMARELO/value"
    sleep 1
    echo "0" > "$SYSFS_DIR/gpio$LED_PIN_AMARELO/value"
    ((cpt++))
done
close



: '
#!/bin/bash

# script baseado no código disponibilizado em:
# Derek Molloy, Exploring Raspberry Pi: Interfacing to the Real World with Embedded Linux,
# Wiley 2016, ISBN 978-1-119-1868-1, http://www.exploringrpi.com/

LED_GPIO=16  # Usar uma variavel facilita alteracoes futuras na porta usada

# funcoes Bash
function setLED
{                                      # $1 eh o primeiro argumento passado para a funcao
	echo $1 >> "/sys/class/gpio/gpio$LED_GPIO/value"
}

# Inicio do programa
if [ $# -ne 1 ]; then                  # se nao houver exatamente um argumento passado ao programa
	echo "Nenhum comando passado. Uso: ./LED.sh command,"
	echo "onde comando pode ser: setup, on, off, status e close"
	echo -e " ex.: ./LED.sh setup, e em seguinda, ./LED.sh on"
	exit 2                         # erro que indica numero invalido de argumentos
fi

echo "O comando passado foi: $1"

if [ "$1" == "setup" ]; then
	echo "Habilitando a GPIO numero $LED_GPIO"
	echo $LED_GPIO >> "/sys/class/gpio/export"
	sleep 1                        # esperar 1 segundo para garantir que a gpio foi exportada
	echo "out" >> "/sys/class/gpio/gpio$LED_GPIO/direction"
elif [ "$1" == "on" ]; then
	echo "Acendendo o LED"
	setLED 1                       # 1 eh recebido como $1 na funcao setLED
elif [ "$1" == "off" ]; then
	echo "Desligando o LED"
	setLED 0                       # 0 eh recebido como $1 na funcao setLED
elif [ "$1" == "status" ]; then
	state=$(cat "/sys/class/gpio/gpio$LED_GPIO/value")
	echo "O estado do LED eh: $state"
elif [ "$1" == "close" ]; then
	echo "Desabilitando a GPIO numero $LED_GPIO"
	echo $LED_GPIO >> "/sys/class/gpio/unexport"
else
	echo "Comando nao reconhecido."
	exit 3                         # erro que indica comando nao reconhecido
fi
'