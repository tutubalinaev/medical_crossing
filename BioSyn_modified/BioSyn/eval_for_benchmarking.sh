#!/usr/bin/env bash

MODEL=model/biosyn-ncbi-disease
MODEL_DIR=${MODEL}
OUTPUT_DIR=.
DATA_DIR=../../MCN_n2c2/processed_pairs/test
DICT_PATH=../../data/vocabs/SNOMEDCT_US-biosyn-aggregated.txt

python3 eval.py \
    --model_dir ${MODEL_DIR} \
    --dictionary_path ${DICT_PATH} \
    --data_dir ${DATA_DIR} \
    --output_dir ${OUTPUT_DIR} \
    --use_cuda \
    --topk 20 \
    --max_length 25 \
    --save_predictions \
    --score_mode sparse