"""
This script was used to create dictionary for MedMentions st21pv dataset
"""
import pandas as pd
import re
from string import punctuation
from tqdm.auto import tqdm

rmv_puncts_regex = re.compile(r'[\s{}]+'.format(re.escape(punctuation)))
def preprocess(s):
    s=str(s)
    s = s.lower()
    phrase = rmv_puncts_regex.split(s)
    phrase = ' '.join(phrase).strip()

    return phrase


ontologies = ["CPT","FMA","GO",
              "HGNC","HPO","ICD10",
              "ICD10CM","ICD9CM","MDR",
              "MSH","MTH","NCBI",
              "NCI","NDDF","NDFRT",
              "OMIM","RXNORM","SNOMEDCT_US"]

print("Reading MRCONSO")
data = pd.read_csv('MRCONSO.RRF', sep='|', header=None)
data = data[data[11].isin(ontologies)]

d = []
cache = data[(data[1] == "ENG")]

for row in tqdm(cache.iterrows()):
    term = preprocess(row[1][14])
    d.append([row[1][0], term])

lines = []
for cui, term in tqdm(d):
    s = str(cui) + '||' + str(term) + '\n'
    lines.append(s)

lines = list(set(lines))
with open("mm_st21pv_dict.txt", 'w') as f:
    f.write(''.join(lines))
