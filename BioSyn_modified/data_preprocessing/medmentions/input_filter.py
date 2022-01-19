"""
This script was used to filter input file by semantic type
"""
from tqdm.auto import tqdm

with open('mm_st21pv_input_prep.concept') as f_in:
    d = f_in.read()

target_group="DISO"
new_lines=[]

for i, s in tqdm(enumerate(d.split('\n'))):
    if len(s) == 0:
        continue

    els = s.split("||")
    if els[2] == target_group:
        new_lines.append(s)

out_dir = 'mm_st21pv_input_prep_filter_' + target_group +".concept"
with open(out_dir, 'w') as f:
    f.write('\n'.join(new_lines))
