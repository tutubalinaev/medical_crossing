#!/usr/bin/env bash


if [ -n "$1" ]; then
  export MRSTY_RRF=$1
else
  export MRSTY_RRF="MRSTY.RRF"
  echo "Warning: MRSTY.RRF path not provided, setting as 'MRSTY.RRF'."
fi

if [ ! -f $MRSTY_RRF ]; then
    echo "File $MRSTY_RRF not found! Stopping."
    exit
fi

## According to the description of the [CLEF2013 task](https://sites.google.com/site/shareclefehealth/)
## This
    # curl https://lhncbc.nlm.nih.gov/semanticnetwork/download/SemGroups.txt | grep DISO | grep -v Finding | cut -f3 -d\| | tr '\n' '|'
## returns these codes that are of interest to us:
## T020|T190|T049|T019|T047|T050|T037|T048|T191|T046|T184

grep "|\(T020\|T190\|T049\|T019\|T047\|T050\|T037\|T048\|T191\|T046\|T184\)" $MRSTY_RRF > MRSTY_DISO.RRF

python3 utils/scripts/clef2013_select_vocab.py \
                            --umls_root ./ \
                            --result_file ./SNOMEDCT_US_clef2013-unaggregated.txt

python3 utils/scripts/aggregate_vocabulary.py \
                                --unagg_file ./SNOMEDCT_US_clef2013-unaggregated.txt \
                                --result_file data/vocabs/SNOMEDCT_US_clef2013-biosyn-aggregated.txt
echo "Lines after aggregation:"
wc -l data/vocabs/SNOMEDCT_US_clef2013-biosyn-aggregated.txt

rm MRSTY_DISO.RRF ./SNOMEDCT_US_clef2013-unaggregated.txt