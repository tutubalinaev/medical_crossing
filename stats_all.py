# coding: utf-8
import os
import pandas as pd
import re

from stats_per_folder import compute_by_folder

RE_D = re.compile('\d')

extensions = ["-fair_levenshtein_0.2/", "-fair_exact/", "-fair_exact_vocab/", "-fair_levenshtein_train_0.2/"]

paths_of_interest = [

    {"name": "MANTRA-de",
     "test": "data/datasets/mantra/de/DISO",
     },
    {"name": "MANTRA-en",
     "test": "data/datasets/mantra/en/DISO",
     },
    {"name": "MANTRA-es",
     "test": "data/datasets/mantra/es/DISO",
     },
    {"name": "MANTRA-fr",
     "test": "data/datasets/mantra/fr/DISO",
     },
    {"name": "MANTRA-nl",
     "test": "data/datasets/mantra/nl/DISO",
     },

    {"name": "CANTEMIST",
     "train": "data/datasets/cantemist/train-set/cantemist-norm-concepts",
     "test": "data/datasets/cantemist/test-set/cantemist-norm-concepts",
     },

    {"name": "codiesp-d",
     "train": "data/datasets/codiesp/DIAGNOSTICO/train",
     "test": "data/datasets/codiesp/DIAGNOSTICO/test",
     },

    {"name": "codiesp-p",
     "train": "data/datasets/codiesp/PROCEDIMIENTO/train",
     "test": "data/datasets/codiesp/PROCEDIMIENTO/test",
     },

    {"name": "mcn",
     "train": "data/datasets/MCN_n2c2/biosyn_processed_pairs/train",
     "test": "data/datasets/MCN_n2c2/biosyn_processed_pairs/test",
     },
]

if __name__ == "__main__":

    dataframe = []

    for path_bunch in paths_of_interest:

        base_directory_test = path_bunch["test"] + "/"
        print("\n\nBase test directory:", base_directory_test)

        # train
        train_stats = None
        unique_ids_train = None

        try:
            base_train_directory = path_bunch["train"] + "/"

            if not os.path.exists(base_train_directory):
                print(f"Path {base_train_directory} doesn't exist.")
                continue

            train_stats, unique_ids_train = compute_by_folder(base_train_directory)
            train_stats["dir"] = base_train_directory
            dataframe.append(train_stats)
        except:
            print("train set not available")

        # test

        if not os.path.exists(base_directory_test):
            print(f"Path {base_directory_test} doesn't exist.")
            raise Exception()

        test_stats, unique_ids_test = compute_by_folder(base_directory_test)
        test_stats["dir"] = base_directory_test
        dataframe.append(test_stats)

        ## full

        if train_stats is None:
            full_stats = test_stats.copy()
            full_stats["avg_numbers"] = "%.2f" % ((test_stats["sum_chars"]) / full_stats["number_of_mentions"])
            full_stats["have_numbers"] = "%2.2f\\%%" % (test_stats["have_numbers"] / full_stats["number_of_mentions"] * 100)
        else:
            full_stats = {}
            full_stats["number_of_mentions"] = train_stats["number_of_mentions"] + test_stats["number_of_mentions"]
            full_stats["number_of_concepts"] = len(unique_ids_test.union(unique_ids_train))
            have_numbers = train_stats["have_numbers"] + test_stats["have_numbers"]
            full_stats["have_numbers"] = "%2.2f\\%%" % (have_numbers / full_stats["number_of_mentions"] * 100)
            full_stats["avg_numbers"] = "%.2f" % (
                        (train_stats["sum_chars"] + test_stats["sum_chars"]) / full_stats["number_of_mentions"])
            full_stats["intersect_train"] = len(unique_ids_train.intersection(unique_ids_test))

        full_stats["dir"] = "FULL"
        dataframe.append(full_stats)
        current_stats = {}

        for extension in extensions:
            directory = path_bunch["test"] + extension

            if not os.path.exists(directory):
                print(f"Path {directory} doesn't exist.")
                continue

            stats, unique_ids = compute_by_folder(directory)
            stats["dir"] = directory
            stats["number_of_mentions"] = f"({stats['number_of_mentions']}) %2.1f\\%%" % (100 *
                                                                                        stats['number_of_mentions'] /
                                                                                        test_stats["number_of_mentions"])
            if unique_ids_train is not None:
                stats["intersect_train"] = len(unique_ids_train.intersection(unique_ids))

            dataframe.append(stats)

    df = pd.DataFrame(dataframe)
    df.to_csv("datasets_stats.csv", index=None)
