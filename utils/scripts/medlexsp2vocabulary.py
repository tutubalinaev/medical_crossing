# coding: utf-8
"""
    MedLexSp debug sample can be obtained here:
    http://www.lllf.uam.es/ESP/nlpdata/wp1/MedLexSp-sample.dsv
"""

from tqdm import tqdm
from argparse import ArgumentParser
from collections import defaultdict

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--dsv_input", default="../../data/vocabs/MedLexSp-sample.dsv")
    parser.add_argument("--output", default="../../data/vocabs/MedLexSp-sample.txt")
    args = parser.parse_args()
    agg = defaultdict(lambda: [])

    with open(args.dsv_input, "r+", encoding="utf-8") as rf:
        for line in tqdm(rf):
            line = line.strip().split("|")
            cui, lemma, options = line[0], line[1].lower().strip(), line[2].split(";")
            agg[lemma].append(cui)
            for o in options:
                agg[o.strip().lower()].append(cui)

    with open(args.output, "w+", encoding="utf-8") as wf:
        for concept_name in agg:
            cuis = "|".join(list(set(agg[concept_name])))
            wf.write("%s||%s\n" % (cuis, concept_name))