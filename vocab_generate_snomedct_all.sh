#!/usr/bin/env bash

if [ -n "$1" ]; then
  export MRCONSO_RRF=$1
else
  export MRCONSO_RRF="MRCONSO.RRF"
  echo "Warning: MRCONSO.RRF path not provided, setting as 'MRCONSO.RRF'."
fi

if [ ! -f $MRCONSO_RRF ]; then
    echo "File $MRCONSO_RRF not found! Stopping."
    exit
fi

grep '|SNOMEDCT_US|' $MRCONSO_RRF > MRCONSO_SNOMEDCT_US.RRF
cut -f1,15 -d\| MRCONSO_SNOMEDCT_US.RRF  | tr \| \\t | sed -e 's/\t/||/g' | sort | uniq > data/vocabs/SNOMEDCT_US-all.txt
python3 utils/scripts/aggregate_vocabulary.py \
                                --unagg_file data/vocabs/SNOMEDCT_US-all.txt \
                                --result_file data/vocabs/SNOMEDCT_US-all-aggregated.txt
echo "Lines after aggregation:"
wc -l data/vocabs/SNOMEDCT_US-all-aggregated.txt
rm MRCONSO_SNOMEDCT_US.RRF data/vocabs/SNOMEDCT_US-all.txt