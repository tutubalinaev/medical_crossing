import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import json

from random import choice, sample
from tqdm.auto import tqdm

data = []
for chunk in tqdm(pd.read_csv('../MRCONSO.RRF', sep='|', header=None, chunksize=1000000), total=15479755/1000000):
    data.append(chunk[chunk[1] == "ENG"])

data = pd.concat(data, )

cui2mention = {}
with open("dataset.concept") as f:
    fdata = f.read().split("\n")
cuis = [x.split("||")[4] for x in fdata]
not_included_counter = 0
cuis = list(set(cuis))
for i,cui in enumerate(cuis):
    #print(cui)
    list_mentions = data[(data[0] == cui) & (data[11] == "SNOMEDCT_US")][14].to_list()
    if len(list_mentions) == 0 :
        not_included_counter += 1
        continue
    term = list_mentions[0]
    cui2mention[cui] = term
    print(f"Processed {i}/{len(cuis)}. Not included: {not_included_counter}")

to_file = "\n".join([f"{c}||{m}"  for c,m in cui2mention.items()])
with open("dictionary.txt", 'w') as f:
    f.write(to_file)
