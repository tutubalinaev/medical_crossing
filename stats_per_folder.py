# coding: utf-8

import os
import re

RE_D = re.compile('\d')


def count_everything(pairs):
    ids = [c for n, c in pairs]
    have_numbers = [1 if RE_D.search(n) is not None else 0 for n, c in pairs]
    lengths = [len(s) for s, c in pairs]

    return {"number_of_mentions": len(pairs),
            "number_of_concepts": len(set(ids)),
            "have_numbers": sum(have_numbers),
            # "have_numbers": "%2.2f%%" % (sum(have_numbers) / len(pairs) * 100),
            # "avg_chars": "%.2f" % np.mean(lengths)
            "sum_chars": sum(lengths)
            }, set(ids)


def compute_by_folder(directory):
    pairs = []
    for file in os.listdir(directory):
        lines = [l.strip().split("||") for l in open(directory + file, "r", encoding="utf-8") if l.strip()]
        pairs.extend([(l[3], l[4]) for l in lines])

    stats = count_everything(pairs)
    return stats
