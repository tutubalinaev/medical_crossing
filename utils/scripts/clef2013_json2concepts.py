# coding: utf-8
import json
import os

"""
DESIRED:
N007||792|800||Entity||vomiting||C0042963||||
N008||850|858||Entity||afebrile||C0277797||||

AVAILABLE:

{"document_id": "05163-019624-DISCHARGE_SUMMARY.txt", 
"text": "9748\t||||\t24307\t||||\t18250\t||||\tDISCHARGE_SUMMARY\t||||\t2011-01-19 00:00:00.0\t||||\t\t||||\t\t||||\t\t||||\t\nAdmission Date: ... (End of Report)\n\n", "label": null, "shift": null, 
"entities": {
...
"T63": {
    "entity_id": "T63", "text": "plaque rupture", 
    "start": 5145, "end": 5159, 
    "type": "Disease_Disorder", "label": "CUI-less", "note": null, "concept_name": null
    }}, 
"relations": []}
"""

CLEF_PATH = "data/datasets/clef2013ehealth/"
CLEF_CONCEPTS_PATH = CLEF_PATH + "pairs/"

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True)
    args = parser.parse_args()

    INPUT_DIR = args.input_dir
    segments = ["train", "test"]

    for segment in segments:
        os.makedirs(CLEF_CONCEPTS_PATH + segment, exist_ok=True)

    for segment in segments:

        for doc_idx, line in enumerate(open(INPUT_DIR + "/" + segment + ".json", "r+", encoding="utf-8")):

            document = json.loads(line.strip())
            new_filename = CLEF_CONCEPTS_PATH + segment + "/" + \
                           document["document_id"].replace(".txt", f"-{segment}-{doc_idx}.concept")

            # N007||792|800||Entity||vomiting||C0042963||||
            entities_ids = [(id, "T%03d" % (int(id.replace("T", "")))) for id in document["entities"].keys()]

            with open(new_filename, "w+", encoding="utf-8") as wf:
                for old_entity_id, fixed_entity_id in sorted(entities_ids, key=lambda x: x[1], reverse=False):
                    e = document["entities"][old_entity_id]
                    text = e['text'].replace("\n", " ")
                    writing = f"{fixed_entity_id}||{e['start']}|{e['end']}||{e['type']}||{text}||{e['label']}||||\n"
                    wf.write(writing)

            with open(new_filename.replace(".concept", ".txt"), "w+", encoding="utf-8") as wf:
                wf.write(document["text"])
