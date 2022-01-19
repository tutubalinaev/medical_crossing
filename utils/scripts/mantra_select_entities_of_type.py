# coding: utf-8

import os
from argparse import ArgumentParser
import shutil

parser = ArgumentParser()
parser.add_argument("--path", default="data/datasets/mantra/")
parser.add_argument("--entity_type", default="DISO")
parser.add_argument("--test_percentage", default=0.3)
args = parser.parse_args()

for lang in os.listdir(args.path):
    if not lang.endswith("txt") and not "_" in lang:

        entity_path = args.path + lang + "/" + args.entity_type + "/"
        os.makedirs(entity_path + "train/", exist_ok=True)
        os.makedirs(entity_path + "test/", exist_ok=True)
        train_count, test_count = 0, 0.0000001

        for concept_file in os.listdir(entity_path):

            if not concept_file.endswith("concept"):
                continue

            lines = len(list(open(entity_path + concept_file, "r", encoding="utf-8").readlines()))

            if test_count / (train_count + test_count) > args.test_percentage:
                shutil.copyfile(entity_path + concept_file, entity_path + "/train/" + concept_file)
                train_count += lines
            else:
                shutil.copyfile(entity_path + concept_file, entity_path + "/test/" + concept_file)
                test_count += lines

        print(lang, train_count, ":", test_count)
