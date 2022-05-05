# coding: utf-8
"""
    For fair evaluation, we exclude duplicates of concept mentions which are present
     both in train and test sets, from test set, using 2 approaches:

     - exact match of the mention
     - levenshtein score
"""
import os
from argparse import ArgumentParser

from tqdm import tqdm

from utils.scripts import filter_by_levenshtein


def read_all_concept_files(directory: str):
    texts = []

    for concept_file in os.listdir(directory):
        for line in open(directory + "/" + concept_file, "r+", encoding="utf-8"):
            texts.append(line.split("||")[3].lower().strip())

    return texts


if __name__ == "__main__":
    import logging
    import sys

    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    parser = ArgumentParser()
    parser.add_argument("--train_dir", default=None, type=str, help="The training data directory with *.concept files.")
    parser.add_argument("--vocabulary", required=True, type=str, help="A path to a vocabulary file.")
    parser.add_argument("--test_dir", required=True, type=str, help="The test data directory with *.concept files.")
    parser.add_argument("--levenshtein_norm_method", default=1, type=int,
                        help="Edit distance normalization method; should be set to 1 to reproduce the approach used "
                             "in the paper: Levenshtein distance divided by the length of the longest string")
    parser.add_argument("--levenshtein_threshold", default=0.2, type=float,
                        help="Cutoff threshold for normalized Levenshtein distance.")

    args = parser.parse_args()

    # reading train data if available
    if args.train_dir is not None:
        train_texts = sorted(list(set(read_all_concept_files(args.train_dir))))
        logging.info(f"---\nA total of {len(train_texts)} unique concept mentions in TRAIN: {args.train_dir}.")
    else:
        train_texts = None
        logging.info("Train dir is not set.")

    # reading vocabulary
    vocab_texts = sorted(
        list(set([line.strip().split("||")[1].lower() for line in open(args.vocabulary, "r", encoding="utf-8")])))
    logging.info(f"---\nA total of {len(vocab_texts)} unique concept mentions in VOCAB: {args.vocabulary}.")

    tree_vocab = filter_by_levenshtein.Tree(vocab_texts)
    vocab_texts = set(vocab_texts)

    # training set filtering
    if train_texts is not None:
        tree_train = filter_by_levenshtein.Tree(train_texts)
        train_texts_set = set(train_texts)
    else:
        train_texts_set = None


    def exact_match_train(name):
        return name in train_texts_set


    def exact_match_vocab(name):
        return name in vocab_texts


    def levenshtein_match_vocab(mention):
        max_dist = int((len(mention)) * args.levenshtein_threshold) + 2
        found_vocab_entries = tree_vocab.search(mention, max_dist)
        resulting_vocab_entries = filter_by_levenshtein.filter_entries(mention,
                                                                       found_vocab_entries,
                                                                       args.levenshtein_threshold,
                                                                       args.levenshtein_norm_method)
        logging.info(f"{mention}  duplicates: {resulting_vocab_entries}")

        # if we have found fuzzy duplicates, we should not keep this item in a test set
        return len(resulting_vocab_entries) > 0

    def levenshtein_match_train(mention):
        # yes i know this is bad and ugly, but the deadline is tomorrow okay?
        max_dist = int((len(mention)) * args.levenshtein_threshold) + 2
        found_vocab_entries = tree_train.search(mention, max_dist)
        resulting_vocab_entries = filter_by_levenshtein.filter_entries(mention,
                                                                       found_vocab_entries,
                                                                       args.levenshtein_threshold,
                                                                       args.levenshtein_norm_method)

        logging.info(f"{mention}  duplicates: {resulting_vocab_entries}")

        # if we found fuzzy duplicates, we should not keep this item in a test set
        return len(resulting_vocab_entries) > 0

    methods_setup = [
        # needs vocab
        {"appendix": f"-fair_exact_vocab",
         "counter_saved": 0,
         "unique_names": set([]),
         "method": exact_match_vocab},

        # needs vocab
        {"appendix": f"-fair_levenshtein_{args.levenshtein_threshold}",
         "counter_saved": 0,
         "unique_names": set([]),
         "method": levenshtein_match_vocab},
    ]

    lev, eq = 1, 0

    if train_texts is not None:
        methods_setup.extend([
            # needs train_set
            {"appendix": f"-fair_exact", "counter_saved": 0, "unique_names": set([]), "method": exact_match_train},
            # needs train_set
            {"appendix": f"-fair_levenshtein_train_{args.levenshtein_threshold}", "counter_saved": 0,
             "unique_names": set([]), "method": levenshtein_match_train}]
        )

    for item in methods_setup:
        item["path"] = args.test_dir.strip("/") + item["appendix"]
        os.makedirs(item["path"], exist_ok=True)

    counter_total, unique_total = 0, set([])

    for concept_file in tqdm(os.listdir(args.test_dir), "test concept files"):

        for item in methods_setup:
            item["writer"] = open(item["path"] + "/" + concept_file, "w+", encoding="utf-8")

        for line in open(args.test_dir + "/" + concept_file, "r", encoding="utf-8"):
            mention = line.split("||")[3].lower().strip()
            unique_total.add(mention)
            counter_total += 1

            # bad bad code but im in a hurry okaY?
            if methods_setup[eq]["method"](mention):
                pass  # for clarity okay?
            else:
                methods_setup[eq]["writer"].write(line.strip() + "\n")
                methods_setup[eq]["counter_saved"] += 1
                methods_setup[eq]["unique_names"].add(mention)

                # because we shouldn't check levenshtein if the exact match is there
                if methods_setup[lev]["method"](mention):
                    pass
                else:
                    methods_setup[lev]["writer"].write(line.strip() + "\n")
                    methods_setup[lev]["counter_saved"] += 1
                    methods_setup[lev]["unique_names"].add(mention)

            # checking by train
            for checker in methods_setup[lev + 1:]:
                if checker["method"](mention):
                    # unfortunately, there is a duplicate somewhere
                    break
                else:
                    checker["writer"].write(line.strip() + "\n")
                    checker["counter_saved"] += 1
                    checker["unique_names"].add(mention)

    # living dengerously
    with open("fairification_stats.out", "a", encoding="utf-8") as wf:

        wf.write(f"{args.test_dir}\t{args.vocabulary}\n{counter_total}\t{len(unique_total)}\n")

        logging.info(f"TOTAL STATS: {counter_total} unique: {len(unique_total)} in {args.test_dir}")

        for item in methods_setup:
            item["writer"].close()
            del item["writer"]
            del item["appendix"]
            del item["method"]
            item["unique_names"] = len(item["unique_names"])
            logging.info(str(item))
            wf.write(f"{item['counter_saved']}\t{item['unique_names']}\t{item['path']}\n")

        wf.write("\n")
