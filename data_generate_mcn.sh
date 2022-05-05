#!/usr/bin/env bash

mkdir data/datasets/MCN_n2c2/processed_test/
mkdir data/datasets/MCN_n2c2/processed_train/

python3 utils/scripts/mcn_process.py --file_list data/datasets/MCN_n2c2/test/test_file_list.txt \
                    --annotation_paths data/datasets/MCN_n2c2/gold/test_norm/ \
                    --note_paths data/datasets/MCN_n2c2/test/test_note/ \
                    --save_to data/datasets/MCN_n2c2/processed_test/

python3 utils/scripts/mcn_process.py --file_list data/datasets/MCN_n2c2/train/train_file_list.txt \
                    --annotation_paths data/datasets/MCN_n2c2/train/train_norm/ \
                    --note_paths data/datasets/MCN_n2c2/train/train_note/ \
                    --save_to data/datasets/MCN_n2c2/processed_train/