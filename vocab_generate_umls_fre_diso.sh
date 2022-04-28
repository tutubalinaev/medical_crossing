#!/usr/bin/env bash

python3 utils/scripts/filter_umls.py --mrconso ./MRCONSO.RRF --mrsty ./MRSTY.RRF \
  --types T020 T190 T049 T019 T047 T050 T033 T037 T048 T191 T046 T184 \
  --save_to ./data/vocabs/umls_fre_diso.txt --lang FRE