#!/usr/bin/env bash

rm -r codiesp.zip codiesp

# https://zenodo.org/record/3837305#.YVwaJX1n02w
# we have used v4 (final as of October 2021)
# this code donwloads the latest one from Zenodo
echo "Loading codiesp.zip from Zenodo..."
zenodo_get 3837305
unzip codiesp.zip
mkdir codiesp

mv final_dataset_v4_to_publish/train/trainX.tsv codiesp/
mv final_dataset_v4_to_publish/test/testX.tsv codiesp/
mv final_dataset_v4_to_publish/dev/devX.tsv codiesp/
rm -r final_dataset_v4_to_publish

python3 utils/scripts/codiesp_converter.py --path codiesp/trainX.tsv \
                                          --segment train \
                                          --output_path data/datasets/codiesp/

python3 utils/scripts/codiesp_converter.py --path codiesp/testX.tsv \
                                          --segment test \
                                          --output_path data/datasets/codiesp/

python3 utils/scripts/codiesp_converter.py --path codiesp/devX.tsv \
                                          --segment dev \
                                          --output_path data/datasets/codiesp/

rm -r codiesp.zip codiesp