import os
from argparse import ArgumentParser

from nltk.tokenize import word_tokenize


def parse_annotation_line(note, line):
    # id||cui||char start||char end
    splitted_line = line.strip().split("||")
    annotation = {"entity": "",
                  "id": splitted_line[0],
                  "cui": splitted_line[1],
                  "start_positions": [],
                  "end_positions": []}

    for i in range(2, len(splitted_line), 2):
        annotation["start_positions"].append(int(splitted_line[i]))
        annotation["end_positions"].append(int(splitted_line[i + 1]))

    entity = ""

    for start, end in zip(annotation["start_positions"], annotation["end_positions"]):
        entity += note[start:end]

    annotation["entity"] = entity

    return annotation


def read_note(note_path):
    with open(note_path, encoding="utf-8") as input_stream:
        note = input_stream.read()
    return note


def read_annotations(note, annotation_path):
    with open(annotation_path, encoding="utf-8") as input_stream:
        annotations = [parse_annotation_line(note, line) for line in input_stream]
    return annotations


def get_n_words_from_context(context, left, n):

    tokenized_context = word_tokenize(context)

    if left:
        n_words = tokenized_context[-n:]
    else:
        n_words = tokenized_context[:n]
    return " ".join(n_words)


def get_mention(note, annotation):

    entity = ""

    for start, end in zip(annotation["start_positions"], annotation["end_positions"]):
        entity += note[start:end]

    return entity


def save_annotations(annotations, save_to):

    with open(save_to, "w+") as fout:
        for ann in annotations:
            start_pos = "|".join([str(x) for x in ann["start_positions"]])
            end_pos = "|".join([str(x) for x in ann["end_positions"]])
            entity = ann["entity"].replace("\n", " ")
            fout.write("{}||{}|{}||Entity||{}||{}\n".format(ann["id"],
                                                            start_pos, end_pos,
                                                            entity, ann["cui"]))


def save_note(note, save_to):
    with open(save_to, "w+", encoding="utf-8") as output_stream:
        output_stream.write(note)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--file_list", default="test/test_file_list.txt")
    parser.add_argument("--annotation_paths", default="test/test_norm_cui_replaced_with_unk/")
    parser.add_argument("--note_paths", default="test/test_note/")
    parser.add_argument("--save_to")
    args = parser.parse_args()

    with open(args.file_list, encoding="utf-8") as input_stream:
        files_list = [line.strip() for line in input_stream]

    annotation_paths = [os.path.join(args.annotation_paths, fl) + ".norm" for fl in files_list]
    note_paths = [os.path.join(args.note_paths, fl) + ".txt" for fl in files_list]

    med_entities,labels = [], []
    left_contexts, right_contexts = [], []
    context_size = 20

    for annotation_path, note_path in zip(annotation_paths, note_paths):
        print("Parsed", annotation_path, note_path)
        note = read_note(note_path)
        annotations = read_annotations(note, annotation_path)
        save_to = args.save_to + os.path.basename(note_path)
        save_annotations(annotations, save_to.replace("txt", "concept"))
        save_note(note, save_to)
