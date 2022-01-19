#!/usr/bin/env bash

rm -r QUAERO_FrenchMed_brat
wget https://quaerofrenchmed.limsi.fr/QUAERO_FrenchMed_brat.zip
unzip QUAERO_FrenchMed_brat.zip

# the same in BioC format
  #rm -r QUAERO_FrenchMed_BioC
  #wget https://quaerofrenchmed.limsi.fr/QUAERO_FrenchMed_BioC.zip
  #unzip QUAERO_FrenchMed_BioC.zip

for SEGMENT in train test dev; do
  for DATA in EMEA MEDLINE; do
    python3 utils/scripts/quaero_brat2concept.py --types DISO --src QUAERO_FrenchMed/corpus/$SEGMENT/$DATA --dest data/datasets/quaero_DISO/$DATA/$SEGMENT
  done
done

rm -r QUAERO_FrenchMed QUAERO_FrenchMed_brat.zip