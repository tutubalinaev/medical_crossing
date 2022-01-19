#!/usr/bin/env bash

ROOT_DIR=`pwd`

echo "Running from" $ROOT_DIR

echo "== MCN =="
for segment in "train" "test"; do
  echo "Processing segment" $segment
  cd $ROOT_DIR/BioSyn_modified/BioSyn/preprocess && python3.6 query_preprocess.py \
              --input_dir $ROOT_DIR/data/datasets/MCN_n2c2/processed_pairs/${segment}/  \
              --output_dir $ROOT_DIR/data/datasets/MCN_n2c2/biosyn_processed_pairs/${segment}/ \
              --ab3p_path ../Ab3P/identify_abbr --lowercase true --remove_punctuation true
done

echo "== clef2013 =="
for segment in "train" "test"; do
  echo "Processing segment" $segment
  cd $ROOT_DIR/BioSyn_modified/BioSyn/preprocess && python3.6 query_preprocess.py \
              --input_dir $ROOT_DIR/data/datasets/clef2013ehealth/pairs/${segment}/  \
              --output_dir $ROOT_DIR/data/datasets/clef2013ehealth/biosyn_processed_pairs/${segment}/ \
              --ab3p_path ../Ab3P/identify_abbr --lowercase true --remove_punctuation true
done