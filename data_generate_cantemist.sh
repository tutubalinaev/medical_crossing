#!/usr/bin/env bash

# https://zenodo.org/record/3978041#.YYlmQLpn02w
zenodo_get 3978041

rm -r data/datasets/cantemist
mkdir data/datasets/cantemist

unzip cantemist.zip -d data/datasets/cantemist

python3 utils/scripts/cantemist2concept.py

rm cantemist.zip