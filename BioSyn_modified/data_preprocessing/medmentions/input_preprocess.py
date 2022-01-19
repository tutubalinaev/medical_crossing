"""
This script is used to preprocess Mad Mentions ST21pv input before passing it to BioSyn

file "mm_st21pv_input.concept" must be created in "input_create.py"
file "ab3p_result.txt" - result of abbreviation expansion (see "corpus_to_ab3p.py")
"""
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

with open("ab3p_result.txt") as f:
    line = f.read()
lines = line.split("\n")

doc_to_abbr={}
for i in range(len(lines)):
    if lines[i].isnumeric():
        docid = lines[i]

        ind = i + 2
        nextline = lines[ind]
        abbrs = {}
        while nextline[:2] == "  ":
            els = nextline[2:].split("|")
            abbrs[els[0]] = els[1]
            ind += 1
            nextline = lines[ind]

        nextline=lines[ind+1]
        while nextline!="":
            els = nextline[2:].split("|")
            abbrs[els[0]]=els[1]
            ind+=1
            nextline = lines[ind]
        doc_to_abbr[docid] = abbrs

with open("mm_st21pv_input.concept") as f:
    line = f.read()
lines = line.split("\n")

with open("mm_st21pv_dict.txt") as f:
    line = f.read()
dict_entries = line.split("\n")
dict_cuids = [l.split("||")[0] for l in dict_entries]

new_lines = []
for input in tqdm(lines):
    els = input.split("||")
    if len(els) == 1:
        continue
    if els[-3] not in dict_cuids:
        continue
    doc_abbrs = doc_to_abbr[els[0]]
    for abbr in list(doc_abbrs.keys()):
        if abbr in els[3]:
            els[3] = els[3].replace(abbr, doc_abbrs[abbr])
    els[3] = preprocess(els[3])
    new_lines.append("||".join(els))

new_lines = list(set(new_lines))
with open('mm_st21pv_input_prep.concept','w') as f:
    f.write('\n'.join(new_lines))