# coding: utf-8
import os
import pandas as pd

segment = "train"


def get_entity_cui_pairs(processed_data_path="processed_pairs", data_segment="train"):

    entities, cuis = [], []
    path_prefix = f"{processed_data_path}/{data_segment}/"

    for f in os.listdir(path_prefix):
        if f.endswith("concept"):
            for line in open(path_prefix + f, "r+", encoding="utf-8"):
                splitted = line.strip().split("||")
                entities.append(splitted[-2])
                cuis.append(splitted[-1])

    return entities, cuis


def prepare_json_format(processed_data_path="processed_pairs", data_segment="train"):

    path_prefix = f"{processed_data_path}/{data_segment}/"
    documents = []

    for f in os.listdir(path_prefix):
        if f.endswith("concept"):
            txt = open(path_prefix + f.replace(".concept", ".txt"), "r+", encoding="utf-8").read().strip()
            document = {"document_id": (f.replace(".concept", "")),
                        "text": txt,
                        "relations": [],
                        "entities": {},
                        "shift": None}

            # EXAMPLE:
            # "entities": {"T1": {"entity_id": "T1", "text": "Бронхиальная астма, атопическая", "start": 9, "end": 40,
            #                     "type": "Disease", "label": null, "note": null}, "T2":

            for line in open(path_prefix + f, "r+", encoding="utf-8"):
                splitted = line.strip().split("||")
                entity_id = splitted[0]
                entity_dict = {"start": splitted[1].split("|")[0],
                               "end": splitted[1].split("|")[1],
                               "type": splitted[2],
                               "text": splitted[-2],
                               "label": splitted[-1],
                               "entity_id": entity_id}
                # entity_dict["note"] = ???
                document["entities"][entity_id] = entity_dict

            documents.append(document)

    return documents


if __name__ == "__main__":

    import json

    for segment in ["train", "test"]:

        print(segment.upper())
        entities, cuis = get_entity_cui_pairs(processed_data_path="processed_pairs", data_segment=segment)
        df = pd.DataFrame({"entity": entities, "concept": cuis})
        print(df.describe())

        with open(f"processed_pairs/{segment}.json", "w+", encoding="utf-8") as wf:
            train_docs = [json.dumps(j) for j in prepare_json_format(data_segment=segment)]
            wf.write("\n".join(train_docs))
