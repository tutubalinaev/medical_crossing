#!/usr/bin/env bash

if [ -n "$1" ]; then
  export MRCONSO_RRF=$1
else
  export MRCONSO_RRF="MRCONSO.RRF"
  echo "Warning: MRCONSO.RRF path not provided, setting as 'MRCONSO.RRF'."
fi

if [ ! -f $MRCONSO_RRF ]; then
    echo "File '$MRCONSO_RRF' not found! Stopping."
    exit
fi

echo "Reading from UMLS..."
grep '|ICD10CM|' $MRCONSO_RRF > MRCONSO_ICD10CM.RRF
grep '|ICD10PCS|' $MRCONSO_RRF > MRCONSO_ICD10PCS.RRF
cut -f11,15,1 -d\| MRCONSO_ICD10CM.RRF  | tr \| \\t | sed -e 's/\t/|/g' | sort | uniq \
            | sed -e 's/\(.*\)|\(.*\)|\(.*\)/\1|\3|\2/g' > ICD10CM-all-unsplitted.txt
cut -f10,15,1 -d\| MRCONSO_ICD10PCS.RRF  | tr \| \\t | sed -e 's/\t/|/g' | sort | uniq \
            | sed -e 's/\(.*\)|\(.*\)|\(.*\)/\1|\3|\2/g' >> ICD10CM-all-unsplitted.txt

echo "Generating mappings..."
cut -f1,2 -d\| ICD10CM-all-unsplitted.txt | sort | uniq | sed -e 's/|/||/g' > data/vocabs/ICD10CM-all-CUIs.txt
cut -f1,3 -d\| ICD10CM-all-unsplitted.txt | sort | uniq> data/vocabs/ICD10CM-all-mapping.txt
python3 utils/scripts/aggregate_vocabulary.py \
                                --unagg_file data/vocabs/ICD10CM-all-CUIs.txt \
                                --result_file data/vocabs/ICD10CM-all-aggregated.txt
echo "Lines before aggregation:"
wc -l data/vocabs/ICD10CM-all-CUIs.txt

echo "Lines after aggregation:"
wc -l data/vocabs/ICD10CM-all-aggregated.txt

echo "Mapping stuff lines:"
wc -l data/vocabs/ICD10CM-all-mapping.txt

rm MRCONSO_ICD10* ICD10CM-all-unsplitted.txt data/vocabs/ICD10CM-all-CUIs.txt