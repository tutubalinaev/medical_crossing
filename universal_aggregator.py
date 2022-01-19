# coding: utf-8

import importlib
import logging
import os
from argparse import ArgumentParser

import omegaconf
import pandas as pd
from omegaconf import OmegaConf

from utils.output_parsers.base_parser import BaseOutputParser

log = logging.getLogger()


def parse_directory(current_directory: str, parser_name: str):
    prefix = "utils.output_parsers."
    module = importlib.import_module(prefix + ".".join(parser_name.split(".")[:-1]))
    parser_class = getattr(module, parser_name.split(".")[-1])
    directory_processor: BaseOutputParser = parser_class(current_directory)
    parsing_result = directory_processor.read_scores()

    if parsing_result.is_empty():
        return None
    else:
        return parsing_result.to_dict()


def get_important_fields(conf: OmegaConf) -> dict:
    try:
        return {
            "model.name": conf.model.name,
            "dataset.name": conf.dataset.name,
            "dataset.fairness": conf.dataset.get("fairness", ""),
            "vocabulary.name": conf.vocabulary.name,
            "model_directory": conf.model.model_directory
        }
    except omegaconf.errors.ConfigAttributeError as e:
        log.exception(f"Config file parsing problem. Skipping {conf}")
        return {}


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--results_dir", default="results/")
    parser.add_argument("--output_filename", default="raw_results_table.csv")
    args = parser.parse_args()

    raw_results, fields_for_uniq = [], set([])
    dirs_for_removal = []

    for subdir in os.listdir(args.results_dir):

        if not subdir.startswith("sessions_"):
            log.warning(f"Won't process directory {subdir}.")
            continue

        result = {"date": subdir.replace("sessions_", "")}

        current_dir = os.path.join(args.results_dir, subdir)
        config_path = os.path.join(current_dir, ".hydra", "config.yaml")
        configs = OmegaConf.load(config_path)

        # getting the parser class name from configs
        parser_name = configs.model.output_parser

        # reading reported parameters from hydra configs
        parameters = get_important_fields(configs)
        fields_for_uniq.update(parameters.keys())
        result.update(parameters)

        # applying a model-specific parser to the output
        parsing_result = parse_directory(current_dir, parser_name)

        # adding only if ANYTHING useful was parsed
        if parsing_result is not None:
            for k, v in parsing_result.items():
                parsing_result[k] = "%2.2f%%" % (round(v * 10000) / 10000 * 100)

            result.update(parsing_result)
            raw_results.append(result)
        else:
            dirs_for_removal.append(current_dir)

    with open("no_results_dirs.txt", "w+", encoding="utf-8") as wf:
        wf.write("\n".join(dirs_for_removal))

    df = pd.DataFrame(raw_results)
    df = df.sort_values(by="date").drop_duplicates(subset=list(fields_for_uniq), keep="last").reset_index(drop=True)
    df = df.sort_values(by=["dataset.name", "dataset.fairness", "model.name"]).reset_index(drop=True)
    df.to_csv(args.output_filename, index=None, sep=",")
    log.info(f"It is done. Please see file '{args.output_filename}' with {df.shape[0]} rows.")
    print(f"It is done. Please see file '{args.output_filename}' with {df.shape[0]} rows.")
