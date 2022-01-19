# coding: utf-8

"""
T1      0 11    Amyloidosis     E85
T2      330 341 amyloidosis     E85
T3      508 519 amyloidosis     E85
T4      727 738 amyloidosis     E85
T1      189 201 tuberculosis
T1      78 92   cardiomyopathy  I42
"""

import os

dir_prefix = "data/datasets/multinel/"

for language in os.listdir("MultiNEL-corpus/mer_annotations/"):
    os.makedirs(dir_prefix + language, exist_ok=True)
    for brat_file in os.listdir("MultiNEL-corpus/mer_annotations/" + language):
        results = []
        for line in open("MultiNEL-corpus/mer_annotations/" + language + "/" + brat_file, encoding="utf-8"):
            line = line.strip()

            if line and len(line.split("\t")) > 3:
                line = line.split("\t")
                str_id = "N%03d" % int(line[0][1:])
                fromm, too = line[1].split(" ")
                fromm, too = int(fromm), int(too)
                results.append(f"{str_id}||{fromm}|{too}||Entity||{line[2]}||{line[3]}")

        if len(results) > 0:
            with open(f"{dir_prefix}/{language}/{brat_file.replace('.txt', '.concept')}", "w+", encoding="utf-8")as wf:
                wf.write("\n".join(results))
