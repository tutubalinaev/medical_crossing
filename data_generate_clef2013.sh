#!/usr/bin/env bash

echo "CLEF2013 eHealth data should already be downloaded..."

if [ -n "$1" ]; then
  echo "Going to look for CLEF data in '$1'."
else
  echo "Can't move on. Please pass CLEF2013 data folder containing 'train.json' and 'test.json' files as an only argument to this script."
  exit
fi

rm -r data/datasets/clef2013ehealth

python3 utils/scripts/clef2013_json2concepts.py --input_dir $1
