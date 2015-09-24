#!/bin/bash
export  TODAY=${HOSTNAME}_`date '+%Y_%m_%d'`
cd ~/latex
echo $HOSTNAME > envar.tex
latex results.tex
latex results.tex
dvipdfmx -o resultsA4_$TODAY.pdf results.dvi
pdfnup --nup 2x1 resultsA4_$TODAY.pdf --outfile results_$TODAY.pdf
lpr results_$TODAY.pdf -P MPC3001 -o Duplex=DuplexTumble
lpr results_$TODAY.pdf -P MPC3001 -o Duplex=DuplexTumble
lpr results_$TODAY.pdf -P MPC3001 -o Duplex=DuplexTumble
lpr results_$TODAY.pdf -P MPC3001 -o Duplex=DuplexTumble
#put resultsA4_$TODAY.pdf zivkovic
#put resultsA4_$TODAY.pdf reyer
#put resultsA4_$TODAY.pdf liu
#put resultsA4_$TODAY.pdf xu
#put resultsA4_$TODAY.pdf schmitz


