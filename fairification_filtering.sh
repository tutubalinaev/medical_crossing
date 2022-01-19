#!/usr/bin/env bash

THRESHOLD=0.2

# QUAERO EMEA#
#python3 fairification.py --train_dir data/datasets/quaero/EMEA/train \
#                          --test_dir data/datasets/quaero/EMEA/test \
#                          --vocabulary data/vocabs/???
#                          --levenshtein_norm_method 1 \
#                          --levenshtein_threshold $THRESHOLD
#
## QUAERO MEDLINE
#python3 fairification.py --train_dir data/datasets/quaero/MEDLINE/train \
#                          --test_dir data/datasets/quaero/MEDLINE/test \
#                          --vocabulary data/vocabs/???
#                          --levenshtein_norm_method 1 \
#                          --levenshtein_threshold $THRESHOLD

# cantemist
#python3 fairification.py --train_dir data/datasets/cantemist/train-set/cantemist-norm-concepts \
#                          --test_dir data/datasets/cantemist/test-set/cantemist-norm-concepts \
#                          --vocabulary data/vocabs/CANTEMIST-lopez-ubeda-et-al.txt \
#                          --levenshtein_norm_method 1 \
#                          --levenshtein_threshold $THRESHOLD > cantemist-fair.out &


# codiesp
python3 fairification.py --test_dir data/datasets/codiesp/PROCEDIMIENTO/test \
                          --train_dir data/datasets/codiesp/PROCEDIMIENTO/train \
                          --vocabulary data/vocabs/codiesp-p-codes-es.txt \
                          --levenshtein_norm_method 1 \
                          --levenshtein_threshold $THRESHOLD > PROCEDIMIENTO-fair.out &
#
## codiesp
python3 fairification.py --test_dir data/datasets/codiesp/DIAGNOSTICO/test \
                          --train_dir data/datasets/codiesp/DIAGNOSTICO/train \
                          --vocabulary data/vocabs/codiesp-d-codes-es.txt \
                          --levenshtein_norm_method 1 \
                          --levenshtein_threshold $THRESHOLD > DIAGNOSTICO-fair.out &
##
### MCN
#python3 fairification.py --test_dir data/datasets/MCN_n2c2/biosyn_processed_pairs/test \
#                          --train_dir data/datasets/MCN_n2c2/biosyn_processed_pairs/train \
#                          --vocabulary data/vocabs/SNOMEDCT_US-all-aggregated.txt \
#                          --levenshtein_norm_method 1 \
#                          --levenshtein_threshold $THRESHOLD > MCN-fair.out &
##
### CLEF2013
#python3 fairification.py  --test_dir data/datasets/clef2013ehealth/biosyn_processed_pairs/test \
#                          --train_dir data/datasets/clef2013ehealth/biosyn_processed_pairs/train \
#                          --vocabulary data/vocabs/SNOMEDCT_US_clef2013-biosyn-aggregated.txt \
#                          --levenshtein_norm_method 1 \
#                          --levenshtein_threshold $THRESHOLD > clef2013ehealth-fair.out &


#python3 fairification.py --test_dir data/datasets/mantra/de/DISO \
#                          --vocabulary data/vocabs/mantra_de_dict_DISO.txt \
#                          --levenshtein_norm_method 1 \
#                          --levenshtein_threshold $THRESHOLD > de_DISO-fair.out &
##
#python3 fairification.py --test_dir data/datasets/mantra/es/DISO \
#                          --vocabulary data/vocabs/mantra_es_dict_DISO.txt \
#                          --levenshtein_norm_method 1 \
#                          --levenshtein_threshold $THRESHOLD > es_DISO-fair.out &
##
#python3 fairification.py --test_dir data/datasets/mantra/en/DISO \
#                          --vocabulary data/vocabs/mantra_en_dict_DISO.txt \
#                          --levenshtein_norm_method 1 \
#                          --levenshtein_threshold $THRESHOLD > en_DISO-fair.out &
##
#python3 fairification.py --test_dir data/datasets/mantra/nl/DISO \
#                          --vocabulary data/vocabs/mantra_nl_dict_DISO.txt \
#                          --levenshtein_norm_method 1 \
#                          --levenshtein_threshold $THRESHOLD > nl_DISO-fair.out &
##
#python3 fairification.py --test_dir data/datasets/mantra/fr/DISO \
#                          --vocabulary data/vocabs/mantra_fr_dict_DISO.txt \
#                          --levenshtein_norm_method 1 \
#                          --levenshtein_threshold $THRESHOLD > fr_DISO-fair.out &