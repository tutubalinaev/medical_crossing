# coding: utf-8
from argparse import ArgumentParser
from collections import defaultdict
from tqdm import tqdm

parser = ArgumentParser()
parser.add_argument('--unagg_file', default="../data/vocabs/SNOMEDCT_US-biosyn.txt",
                    help="Path to the unaggregated SNOMEDCT_US dictionary", type=str)
parser.add_argument('--result_file', default="../data/vocabs/SNOMEDCT_US-biosyn-aggregated.txt",
                    help="Path to the aggregated SNOMEDCT_US dictionary", type=str)

args = parser.parse_args()

lines = [line.split("||") for line in open(args.unagg_file, "r", encoding="utf-8").readlines()]

dd = defaultdict(lambda: [])

for line in tqdm(lines, "Collecting data"):
    # yes, suboptimal, but i don't want to screw the order
    if line[0] not in dd[line[1].lower()]:
        dd[line[1].lower()].append(line[0])

newlines = []

for entity in tqdm(dd, "Preparing the results"):
    cuis = dd[entity]
    line = ""
    line += "|".join(cuis) + "||"
    line += entity
    newlines.append(line.strip())

with open(args.result_file, "w+", encoding="utf-8") as wf:
    wf.write("\n".join(sorted(newlines)))
