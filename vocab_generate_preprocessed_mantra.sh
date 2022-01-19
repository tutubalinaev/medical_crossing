#!/usr/bin/env bash

unzip mantra_biosyn_splited.zip
mv mantra_biosyn_splited mantra
mv mantra* data/datasets/

python3 utils/scripts/mantra_restructure.py