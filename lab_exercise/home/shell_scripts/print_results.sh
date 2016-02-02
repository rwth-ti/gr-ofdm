#!/bin/bash
export  TODAY=${HOSTNAME}_`date '+%Y_%m_%d'`
export  PRINTER=HPC4700
if ! (lpstat -p $PRINTER ) ;
then 
    echo "WARNING: Printer name may be wrong or printer is offline."
fi
cd ~/latex
echo $HOSTNAME > envar.tex
latex results.tex
latex results.tex
dvipdfmx -o resultsA4_$TODAY.pdf results.dvi
pdfnup --nup 2x1 resultsA4_$TODAY.pdf --outfile results_$TODAY.pdf
if [[ $USER == *"ofdmlab"* ]];
then
    ans=$(zenity --list --column="Persons" 1 2 3 4 --text="How many copies do you need?")

    echo $ans
    echo "copies..."
    if (( $ans > 4 ))
    then
        persons=4
        echo "Not more then 4 copies, please."
    else
        persons=$ans
    fi

    i=1
    echo "printing..."
    while [ "$i" -le "$persons" ];do
        echo $i
        lpr results_$TODAY.pdf -P $PRINTER -o Duplex=DuplexTumble
        let i=i+1
    done

else
    echo "ERROR:No ofdmlab-account! Abort printing."
fi
#put resultsA4_$TODAY.pdf zivkovic
#put resultsA4_$TODAY.pdf reyer
#put resultsA4_$TODAY.pdf liu
#put resultsA4_$TODAY.pdf xu
#put resultsA4_$TODAY.pdf schmitz


