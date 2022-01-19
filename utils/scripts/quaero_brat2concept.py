# coding: utf-8
"""
    Stuff similar to `cantemist2concept.py`

    T1	CHEM 15 29	méthyl-mercure
    #1	AnnotatorNotes T1	C0025794
    T2	LIVB 38 45	Insecte
    #2	AnnotatorNotes T2	C0021585

"""
from collections import defaultdict


def brat2concept(brat_file_path: str, retained_types: set) -> list:

    results, t_id = [], None
    tid2lines = defaultdict(lambda: [])
    current_custom_id = 1

    for line in open(brat_file_path, encoding="utf-8"):
        print(line.strip())

        if line.startswith("T"):
            row = line.strip().split("\t")
            t_id = row[0]

            meta_splitted = row[1].split(" ")
            tyype = meta_splitted[0]
            spans = (" ".join(meta_splitted[1:])).split(";")

            for s in spans:
                fromm, too = int(s.split(" ")[0]), int(s.split(" ")[1])
                str_id = "N%03d" % int(current_custom_id)

                if retained_types is not None and tyype in retained_types:
                    tid2lines[t_id].append(f"{str_id}||{fromm}|{too}||{tyype}||{row[2]}||")
                current_custom_id += 1

        elif line.startswith("#"):
            row = line.strip().split("\t")
            current_t_id = row[1].split(" ")[-1]
            # assert len(tid2lines[current_t_id]) > 0
            for b in tid2lines[current_t_id]:
                results.append(b + row[2] + "||||")

    return sorted(results)


if __name__ == "__main__":

    from argparse import ArgumentParser
    import os

    parser = ArgumentParser()
    parser.add_argument("--src", default="QUAERO_FrenchMed/corpus/train/MEDLINE")
    parser.add_argument("--dest", default="data/datasets/QUAERO_FrenchMed/MEDLINE/train")
    parser.add_argument("--types", default=None) # comma-separated
    args = parser.parse_args()

    try:
        os.makedirs(args.dest, exist_ok=True)
    except:
        pass

    types_of_interest = set(args.types.strip().split(",")) if args.types else None

    for file in os.listdir(args.src):
        if not file.endswith(".ann"):
           continue
        concepts_list = brat2concept(args.src + "/" + file, types_of_interest)

        with open(args.dest + "/" + file.replace(".ann", ".concept"), "w+", encoding="utf-8") as wf:
            wf.write("\n".join(concepts_list))