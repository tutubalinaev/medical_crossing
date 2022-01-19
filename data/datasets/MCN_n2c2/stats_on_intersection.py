# coding: utf-8
from argparse import ArgumentParser
from collections import Counter
import os

MENTION_FIELD_NUMBER = 3


def get_mentions_counts(path: str)-> Counter:
    train_mentions_counter = Counter()
    assert path.endswith("/")

    for f in os.listdir(path):
        if f.endswith(".concept"):
            for line in open(path + f, "r", encoding="utf-8"):
                name = line.strip().split("||")[MENTION_FIELD_NUMBER]
                train_mentions_counter[name] += 1
    return train_mentions_counter


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--train_concepts_path", type=str, default="biosyn_processed_pairs/train/")
    parser.add_argument("--test_concepts_path", type=str, default="biosyn_processed_pairs/test/")
    args = parser.parse_args()

    train_counter = get_mentions_counts(args.train_concepts_path)
    test_counter = get_mentions_counts(args.test_concepts_path)

    print("train mentions as set", len(train_counter.keys()))
    print("test mentions as set ", len(test_counter.keys()))
    intersection = set(train_counter.keys()).intersection(set(test_counter.keys()))
    print("intersection size:   ", len(intersection))

    counts_intersection = [(train_counter[mention], test_counter[mention], mention) for mention in intersection]
    counts_intersection = sorted(counts_intersection, reverse=True)

    for tr,te,m in counts_intersection[:20]:
        print(f"{tr}\t{te}\t{m}")
