# coding: utf-8
import os
from argparse import ArgumentParser
from collections import defaultdict

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--path", default="codiesp/trainX.tsv")
    parser.add_argument("--segment", default="train")
    parser.add_argument("--output_path", default="data/datasets/codiesp/")
    args = parser.parse_args()

    concept_dict = {"DIAGNOSTICO": defaultdict(lambda: []), "PROCEDIMIENTO": defaultdict(lambda: [])}
    count = 0

    for line in open(args.path, "r+", encoding="utf-8"):
        count += 1
        file, clazz, code, evidence, from_to = line.strip().split("\t")
        concept_dict[clazz][file].append((clazz, code.upper(), evidence, from_to))

    for tyype in ["DIAGNOSTICO", "PROCEDIMIENTO"]:

        os.makedirs(args.output_path + "/" + tyype + "/" + args.segment, exist_ok=True)

        for key in concept_dict[tyype]:

            with open(args.output_path + "/" +
                      tyype + "/" +
                      args.segment + "/" +
                      key + ".concept", "w+", encoding="utf-8") as wf:

                for idx, items in enumerate(concept_dict[tyype][key]):
                    id = "N%03d" % (idx + 1)
                    (clazz, code, evidence, from_to) = items

                    # N011||740|744||Entity||pain||C0030193||||
                    line = f"{id}||{from_to}||{clazz}||{evidence}||{code}||||\n"
                    wf.write(line)

    # --- end