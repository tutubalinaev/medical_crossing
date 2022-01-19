"""
This script is used to prepare Mad Mentions ST21pv dataset for passing to Abbreviation Plus Pseudo-Precision (Ab3P)
abbreviation definittion detector
"""
import csv
from tqdm.auto import tqdm

with open("corpus_pubtator_st21pv.txt"):
    path_data = "corpus_pubtator_st21pv.txt"
    with open(path_data) as f:
        reader = csv.reader(f, delimiter="|")
        raw_mm = list(reader)

out_path = "ab3p_result.txt"

lines = []
for meta in tqdm(raw_mm):
    if len(meta)>1:
        if meta[1]=='t':
            lines.append(meta[0])
        lines.append(meta[2])
        if meta[1]=='a':
            lines.append("")

with open(out_path, 'w') as f:
    for l in lines:
        f.write(l+'\n')
