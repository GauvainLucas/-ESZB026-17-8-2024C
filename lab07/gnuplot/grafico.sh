#!/bin/sh
ARQUIVODADOS=/home/pi/ESZB026-17-8-2024C/lab07/gnuplot/dados_retainv.txt
ARQUIVOSAIDA=/home/pi/ESZB026-17-8-2024C/lab07/gnuplot/dados_retainv.png

gnuplot << EOF
set title "Título"
set ylabel "Eixo Y"
set xlabel "Eixo X"
set terminal png
set output "$ARQUIVOSAIDA"
plot "$ARQUIVODADOS" \
     linecolor rgb '#0060ad' \
     linetype 1 \
     linewidth 1 \
     pointtype 2 \
     pointsize 1.0 \
     title "meus dados" \
     with linespoints
EOF

