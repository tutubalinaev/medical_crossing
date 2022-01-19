# coding: utf-8

import os
from collections import defaultdict

ROOT = "../../"

datasets = [{
    "name": "MCN_n2c2",
    "path_train_concepts": ROOT + "data/datasets/MCN_n2c2/biosyn_processed_pairs/train/",
    "path_test_concepts": ROOT + "data/datasets/MCN_n2c2/biosyn_processed_pairs/test/"
}, {
    "name": "CANTEMIST",
    "path_train_concepts": ROOT + "data/datasets/cantemist/train-set/cantemist-norm-concepts/",
    "path_test_concepts": ROOT + "data/datasets/cantemist/test-set/cantemist-norm-concepts/"
}
]

for dataset in datasets:

    print("\n\n--- %s ---" % dataset["name"])
    name2cui = defaultdict(lambda: [])
    test_set_size = 0

    for f in os.listdir(dataset["path_test_concepts"]):
        if f.endswith("concept"):
            for line in open(dataset["path_test_concepts"] + f, encoding="utf-8"):
                splitted = line.strip().split("||")
                name2cui[splitted[3]].append(splitted[4])
                test_set_size += 1

    print("Test items:", test_set_size)
    print("Test names set size:", len(name2cui))
    exact_match_seen, train_set_size = 0, 0
    name2cui_train = defaultdict(lambda: [])

    for f in os.listdir(dataset["path_train_concepts"]):
        if f.endswith("concept"):
            for line in open(dataset["path_train_concepts"] + f, encoding="utf-8"):
                train_set_size += 1
                splitted = line.strip().split("||")
                name2cui_train[splitted[3]].append(splitted[4])
                current_name = splitted[3]

                if current_name in name2cui:
                    # print("[%s]" % splitted[3], "already seen in test!")
                    exact_match_seen += 1
                else:
                    pass
                    # todo: LEVENSTEIN or something else???
                    # for candidate in name2cui.keys():
                    #     if  current_name

    print("Train items:", test_set_size)
    print("Train names set:", len(name2cui_train))
    print("--")
    print("Exact matches in train:", exact_match_seen)
    print("Train/test sets intersection:", len(set(name2cui.keys()).intersection(name2cui_train.keys())))
