"""
This script was used to filter dictionary for MedMentions st21pv dataset by according semantic group
"""
import json

def parse_sem_groups(path):
    d = {}

    with open(path) as file:
        f = file.read()

    for s in f.split('\n'):
        if len(s) == 0:
            continue

        words = s.split('|')

        d[words[2]] = words[0]
    return d

with open('cui_to_type.json') as f:
    types = json.load(f)

groups = parse_sem_groups('SemGroups.txt')

target_group="DISO"

def filter_dict_by_group(in_path, out_path):
    with open(in_path) as f_in:
        d = f_in.read()

    invalid_entries = 0

    with open(out_path, 'w') as f_out:
        for i, s in enumerate(d.split('\n')):
            if len(s) == 0:
                continue

            try:
                cui, _ = s.split('||')
            except:
                print("Invalid string: ", s)

            if cui not in types:
                invalid_entries += 1
                continue

            cui_types = types[cui]

            for t in cui_types:
                if groups[t] == target_group:
                    f_out.write(s + '\n')


dict_in_path = 'mm_st21pv_dict.txt'
dict_out_path = 'mm_st21pv_dict_' + target_group + ".txt"

filter_dict_by_group(dict_in_path, dict_out_path)