#!/usr/bin/env bash

if [ ! -f cieo-synonyms.csv ]; then
    echo "File 'cieo-synonyms.csv' not found! Stopping."
    exit
fi

python3 utils/scripts/cieo_synonyms_preparation_as_is.py

echo "Done."