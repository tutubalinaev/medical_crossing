# coding: utf-8
import json
import logging
import os

from .base_parser import BaseOutputParser, ResultsBundle

log = logging.getLogger()


class JsonSapbertOutputParser(BaseOutputParser):
    """
        Works with SapBert
    """

    def __init__(self, directory: str, stdout_filename="predictions_eval.json", name="sapbert"):
        super().__init__(directory, stdout_filename, name)
        self.filename = stdout_filename
        self.name = name

    def read_scores(self):
        try:
            with open(os.path.join(self.directory, self.stdout_filename), "r", encoding="utf-8") as rf:
                data = json.loads(rf.read())
            assert "acc1" in data and "acc5" in data
            return ResultsBundle(acc1=data["acc1"], acc5=data["acc5"])
        except FileNotFoundError as e:
            log.error(f"Could not find {self.name} output in directory '{self.directory}'. Returning empty results.")
            return ResultsBundle()
