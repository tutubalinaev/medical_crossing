# coding: utf-8

import os
import shutil

template = \
    """name: Mantra (%s, %s)
# could be "-fair_exact", "-fair_levenshtein" or nothing
fairness:
lang: %s
path: ${dataset.base_dir}/mantra/%s/%s"""

path = "data/datasets/mantra/"

for lang in os.listdir(path):
    if len(lang) > 2:
        continue

    for f in os.listdir(path + lang):
        if not "DISO" in f:
            continue
        if f.endswith("txt"):
            filename = "mantra_" + lang + "_" + f
            shutil.copyfile(path + lang + "/" + f, "data/vocabs/" + filename)
        else:
            with open("config/dataset/mantra_%s_%s.yaml" % (lang, f), "w+", encoding="utf-8") as wf:
                wf.write(template % (lang, f, lang, lang, f))
            with open("config/vocabulary/mantra_%s_%s.yaml" % (lang, f), "w+", encoding="utf-8") as wf:
                wf.write("name: MantraGSC (%s, %s)\n" % (lang, f))
                wf.write("path: ${vocabulary.base_dir}/mantra_%s_dict_%s.txt" % (lang, f))
