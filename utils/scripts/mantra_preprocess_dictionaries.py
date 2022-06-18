# coding: utf-8
import os
import re
from collections import defaultdict

from tqdm import tqdm
from string import punctuation

rmv_puncts_regex = re.compile(r'[\s{}]+'.format(re.escape(punctuation)))


def preprocess(s):
    s = s.lower()
    phrase = rmv_puncts_regex.split(s)
    phrase = ' '.join(phrase).strip()

    return phrase


def merge_dict(in_path, out_path):

    with open(in_path, "r", encoding="utf-8") as f:
        data = f.read()

    term_to_cuis = {}

    for line in data.split('\n'):

        try:
            cui, term = line.split('||')
        except:
            print("Invalid string: ", line)

        if term not in term_to_cuis:
            term_to_cuis[term] = [cui]
        else:
            term_to_cuis[term].append(cui)

    with open(out_path, 'w', encoding="utf-8") as f:

        for term, cuis in term_to_cuis.items():
            cui_str = ''
            for cui in cuis:
                cui_str += cui + '|'
            out_str = cui_str + '|' + term + '\n'
            f.write(out_str)


if __name__ == "__main__":

    from_dir = "./"
    to_dir = "data/vocabs/"

    for file in tqdm(os.listdir(from_dir), "files"):

        if file.startswith("mantra_raw"):
            str_set = set()

            out_path = os.path.join(to_dir, file.replace("_raw", "_pre"))
            in_path = os.path.join(from_dir, file)

            with open(in_path, "r", encoding="utf-8") as f:
                data = f.read()

            if file.endswith("txt"):

                with open(out_path, 'w', encoding="utf-8") as f:

                    for line in data.split('\n'):
                        if len(line) == 0:
                            continue

                        try:
                            cui, term = line.split('||')
                            term = preprocess(term)
                            out_str = cui + '||' + term + '\n'

                            if out_str not in str_set:
                                f.write(out_str)
                                str_set.add(out_str)
                        except:
                            print("Invalid string: ", line)

    for file in os.listdir(to_dir):

        if 'mantra_pre' in file:
            str_set = set()
            out_path = os.path.join(to_dir, file.replace("_pre", "_prefinal"))
            in_path = os.path.join(to_dir, file)
            merge_dict(in_path, out_path)
