#!/usr/bin/env bash

#https://zenodo.org/record/3632523#.YV4EVH1n02x
echo "Loading ICD10 from Zenodo... (CLEF2020)"
zenodo_get 3632523

rm -r codiesp_codes
mkdir codiesp_codes
unzip codiesp_codes.zip -d codiesp_codes

python3 utils/scripts/codiesp_vocab_converter.py --file codiesp_codes/codiesp-D_codes.tsv \
                                                --output_es data/vocabs/codiesp-d-codes-es.txt \
                                                --output_en data/vocabs/codiesp-d-codes-en.txt

python3 utils/scripts/codiesp_vocab_converter.py --file codiesp_codes/codiesp-P_codes.tsv \
                                                --output_es data/vocabs/codiesp-p-codes-es.txt \
                                                --output_en data/vocabs/codiesp-p-codes-en.txt

rm -r codiesp_codes codiesp_codes.zip
echo "It is done."