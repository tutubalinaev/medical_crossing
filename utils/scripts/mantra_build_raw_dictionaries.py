# coding: utf-8

import json
import os
import re
from string import punctuation

import pandas as pd
from tqdm import tqdm

rmv_puncts_regex = re.compile(r"[\s{}]+".format(re.escape(punctuation)))


def process_language_dict(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, row in tqdm(enumerate(data.iterrows()), path):
            cui = row[1][0]
            termin = row[1][14]
            if type(cui) != str or type(termin) != str:
                continue
            s = cui + "||" + termin + "\n"
            f.write(s)


def preprocess(s):
    s = s.lower()
    phrase = rmv_puncts_regex.split(s)
    phrase = " ".join(phrase).strip()

    return phrase


def parse_sem_groups(path):
    d = {}

    with open(path, "r", encoding="utf-8") as file:
        f = file.read()

    for s in f.split("\n"):
        if len(s) == 0:
            continue

        words = s.split("|")

        d[words[2]] = words[0]
    return d


def parse_type_file(data):
    d = {}

    for i, row in tqdm(enumerate(data.iterrows())):

        cui, t = row[1][0], row[1][1]

        if cui in d:
            d[cui].append(t)
        else:
            d[cui] = [t]
    return d


def filter_dict_by_group(in_path, out_path, target_group):
    with open(in_path, "r", encoding="utf-8") as f_in:
        d = f_in.read()

    invalid_entries = 0

    with open(out_path, "w", encoding="utf-8") as f_out:
        for i, s in enumerate(d.split("\n")):
            if len(s) == 0:
                continue

            try:
                cui, _ = s.split("||")
            except:
                print("Invalid string: ", s)

            if cui not in types:
                invalid_entries += 1
                continue

            cui_types = types[cui]

            for t in cui_types:
                if groups[t] == target_group:
                    f_out.write(s + "\n")
                    break


if __name__ == "__main__":

    print("Reading MRCONSO.RRF...")

    data = pd.read_csv("./MRCONSO.RRF", sep="|", header=None)

    print("Getting language-specific data from MRCONSO...")

    eng_data = data[(data[11] == "MDR") | (data[11] == "MSH") | (data[11] == "SNOMEDCT_US")]
    fr_data = data[(data[11] == "MDRFRE") | (data[11] == "MSHFRE")]
    es_data = data[(data[11] == "MDRSPA") | (data[11] == "MSHSPA") | (data[11] == "SCTSPA")]
    de_data = data[(data[11] == "MDRGER") | (data[11] == "MSHGER")]
    nl_data = data[(data[11] == "MDRDUT") | (data[11] == "MSHDUT")]

    print("Writing dictionaries for languages...")

    if not os.path.exists("data/vocabs/eng_dictionary.txt"):
        process_language_dict(eng_data, "data/vocabs/eng_dictionary.txt")

    if not os.path.exists("data/vocabs/fr_dictionary.txt"):
        process_language_dict(fr_data, "data/vocabs/fr_dictionary.txt")

    if not os.path.exists("data/vocabs/es_dictionary.txt"):
        process_language_dict(es_data, "data/vocabs/es_dictionary.txt")

    if not os.path.exists("data/vocabs/de_dictionary.txt"):
        process_language_dict(de_data, "data/vocabs/de_dictionary.txt")

    if not os.path.exists("data/vocabs/nl_dictionary.txt"):
        process_language_dict(nl_data, "data/vocabs/nl_dictionary.txt")

    print("Language dictionaries built.")
    print("Reading MRSTY.RRF...")

    data = pd.read_csv("./MRSTY.RRF", sep="|", header=None)

    if not os.path.exists("./data/vocabs/cui_to_type.json"):
        print("Parsing MRSTY...")

        types = parse_type_file(data)
        print("Saving cui-to-type...")

        with open("./data/vocabs/cui_to_type.json", "w") as f:
            result = json.dumps(types, indent=4)
            f.write(result)

    print("Parsing SemGroups...")

    groups = parse_sem_groups("SemGroups.txt")

    print("Reading cui-to-type")

    with open("./data/vocabs/cui_to_type.json") as f:
        types = json.load(f)

    target_groups = "ANAT, CHEM, DEVI, DISO, GEOG, LIVB, OBJC, PHEN, PHYS, PROC".split(", ")
    languages = ["nl", "eng", "fr", "de", "es"]

    print("Filtering dictionaries by language and target group...")

    for target_group in target_groups:
        print("target group:", target_group)
        for language in languages:
            print("language:", language)
            dict_in_path = "./data/vocabs/{}_dictionary.txt".format(language)
            dict_out_path = "./data/vocabs/mantra_raw_{}_dict_{}.txt".format(language, target_group)
            filter_dict_by_group(dict_in_path, dict_out_path, target_group)

    print("It is done.")
