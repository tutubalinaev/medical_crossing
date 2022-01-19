#!/usr/bin/python
"""
    --vocab — словарь, по которому идет фильтрация
    --input_data — входные данные в формате биосин
    --threshold — порог (т.е. остаются только те кейсы ближайший концепт
                        к которым находится на расстоянии не меньше порога)
    --method — способ нормализации расстояния Левенштейна
    --save_to — куда сохранить отфильтрованный сет

    the script was received from Zulfat Miftakhutdinov
"""

import sys
from argparse import ArgumentParser

import distance
from tqdm import tqdm


def read_annotation_file(ann_file_path):
    data = []

    with open(ann_file_path, encoding='utf-8') as input_stream:

        for row_id, line in enumerate(input_stream):

            splitted_line = line.strip().split('||')
            mention = splitted_line[-2]
            concept_id = splitted_line[-1]
            data.append([mention, line])

    return data


class TreeNode:

    def __init__(self):
        self.word = None
        self.children = {}

    def insert(self, word):
        node = self
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TreeNode()
            node = node.children[letter]
        node.word = word


class Tree:

    def __init__(self, vocabulary):
        self.tree = TreeNode()

        if type(vocabulary) == str:
            # is a path
            with open(vocabulary, encoding='utf-8') as input_stream:
                for word in tqdm(input_stream, "loading vocab into tree from path"):
                    self.tree.insert(word.strip())
        elif type(vocabulary) == set or type(vocabulary) == list:
            for word in tqdm(vocabulary, "loading vocab into tree from provided iterable"):
                self.tree.insert(word.strip())
        else:
            raise Exception("Wrong `vocabulary` param type")

    def search(self, word, maxCost):

        # build first row
        currentRow = range(len(word) + 1)
        results = []

        # recursively search each branch of the trie
        for letter in self.tree.children:
            self.searchRecursive(self.tree.children[letter], letter, word, currentRow, results, maxCost)

        return results

    def searchRecursive(self, node, letter, word, previousRow, results, maxCost):

        columns = len(word) + 1
        currentRow = [previousRow[0] + 1]

        # Build one row for the letter, with a column for each letter in the target
        # word, plus one for the empty string at column 0
        for column in range(1, columns):

            insertCost = currentRow[column - 1] + 1
            deleteCost = previousRow[column] + 1

            if word[column - 1] != letter:
                replaceCost = previousRow[column - 1] + 1
            else:
                replaceCost = previousRow[column - 1]

            currentRow.append(min(insertCost, deleteCost, replaceCost))

        # if the last entry in the row indicates the optimal cost is less than the
        # maximum cost, and there is a word in this trie node, then add it.
        if currentRow[-1] <= maxCost and node.word != None:
            results.append((node.word, currentRow[-1]))

        # if any entries in the row are less than the maximum cost, then
        # recursively search each branch of the trie
        if min(currentRow) <= maxCost:
            for letter in node.children:
                self.searchRecursive(node.children[letter], letter, word, currentRow, results, maxCost)


def filter_entries(mention, vocab_entries, threshold, method):

    f = []

    for vocab_entry, _ in vocab_entries:
        if distance.nlevenshtein(vocab_entry, mention, method=method) < threshold:
            f.append(vocab_entry)

    return f


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--vocab')
    parser.add_argument('--input_data')
    parser.add_argument('--threshold', type=float, default=0.3)
    parser.add_argument('--method', type=int, default=1)
    parser.add_argument('--save_to')
    args = parser.parse_args()

    tree, data, count = Tree(args.vocab), read_annotation_file(args.input_data), 0

    with open(args.save_to, 'w', encoding='utf-8') as output_stream:

        for mention, line in tqdm(data, "lines processed"):

            max_dist = int(len(mention) * args.threshold) + 2
            vocab_entries = tree.search(mention, max_dist)
            vocab_entries = filter_entries(mention, vocab_entries, args.threshold, args.method)

            if len(vocab_entries) == 0:
                count += 1
                output_stream.write(line)

    print(f"Saved {count} examples")
