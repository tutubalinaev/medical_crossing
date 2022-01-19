#!/usr/bin/env bash

if [ -n "$1" ]; then
  export MEDLEXSP_ZIP=$1
else
  export MEDLEXSP_ZIP="MedLexSp.zip"
  echo "Warning: $MEDLEXSP_ZIP path not provided, setting as 'MedLexSp.zip'."
fi

if [ ! -f $MEDLEXSP_ZIP ]; then
    echo "File '$MEDLEXSP_ZIP' not found! Stopping."
    exit
fi

unzip $MEDLEXSP_ZIP -d data/vocabs/

python3 utils/scripts/medlexsp2vocabulary.py \
              --dsv_input data/vocabs/MedLexSp/MedLexSp_v0.dsv \
              --output data/vocabs/MedLexSp_v0.txt

rm -r data/vocabs/MedLexSp