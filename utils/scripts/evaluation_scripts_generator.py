# coding: utf-8

from argparse import ArgumentParser

# langs = "de en es fr nl".split(" ")
# types = ["DISO"]
# types = "ANAT CHEM DEVI DISO GEOG LIVB OBJC PHEN PHYS PROC".split(" ")

# data config -> vocab config
MAP_DATA = {
    # "codiesp-d": "codiesp_icd10cm",
    # "codiesp-p": "codiesp_icd10pcs",
    # "mcn_n2c2": "snomedct_us_aggregated",
    # "clef2013ehealth": "snomedct_us_disorders",
    # "cantemist": "cantemist_lopez-ubeda-et-al",
    # "russian_clinical_data": "umls_rus"
    "quaero_DISO_emea": "umls_fr_diso",
    "quaero_DISO_medline": "umls_fr_diso",
}

# for l in langs:
#     for t in types:
#         MAP_DATA[f"mantra_{l}_{t}"] = f"mantra_{l}_{t}"

# quaero_types = ["DISO"]
# for t in quaero_types:
#     MAP_DATA[f"quaero_{t}"] = f"quaero_{t}"

MAP_MODEL = {
    "sapbert_xl": "sapbert",
    "sparse": "biosyn",
    "bert_ranking": "fair_eval",
    "russian_bert_ranking": "fair_eval",
    "spanish_bert_ranking": "fair_eval",
    "spanish_bio_bert_ranking": "fair_eval",
    # camembert something : fair_eval
}

fairnesses = reversed([""]) #"-fair_exact","-fair_exact_vocab", "-fair_levenshtein_0.2", "-fair_levenshtein_train_0.2", ""])
models = ["sparse"]

parser = ArgumentParser()
parser.add_argument("--dataset", type=str, default="quaero_DISO_emea")
parser.add_argument("--device", type=int, default=2)

args = parser.parse_args()

with open(f"evaluate_data-{args.dataset}_on-{args.device}.sh", "w+", encoding="utf-8") as wf:
    wf.write("#!/usr/bin/env bash\n\n")
    for model in models:
        for fairness in fairnesses:
            call = f"CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES={args.device} python3 " + \
                   f"universal_runner.py parameters_mapping={MAP_MODEL[model]} model={model} " + \
                   f"dataset={args.dataset} dataset.fairness={fairness} vocabulary={MAP_DATA[args.dataset]}\n"
            wf.write(call)
