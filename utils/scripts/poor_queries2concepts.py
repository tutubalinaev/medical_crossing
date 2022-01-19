# coding: utf-8

import argparse
import os

if __name__ == "__main__":

    original_queries_path = "../../data/datasets/xbel_v0.0"
    files = [original_queries_path + "/" + f for f in os.listdir(original_queries_path) if f.endswith("txt")]
    result, i = [], 0

    for file in files:
        with open(file.replace(".txt", ".concept"), "w+", encoding="utf-8") as wf:
            for line in open(file, encoding="utf-8"):
                cuis, text = line.split("||")
                cuis = cuis.split("|")
                for cui in cuis:
                    # 9288106 | | 254 | 273 | | DiseaseClass | | lymphoid neoplasias | | D008223
                    wf.write("%d||from|to||Entity||%s||%s\n" % (i, text.strip(), cui))
                    i += 1