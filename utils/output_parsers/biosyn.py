# coding: utf-8
import logging

from .sapbert_json import JsonSapbertOutputParser

log = logging.getLogger()


class BioSynOutputParser(JsonSapbertOutputParser):

    def __init__(self, directory: str, stdout_filename="predictions_eval.json", name="biosyn"):
        super().__init__(directory, stdout_filename, name)
        self.filename = stdout_filename
        self.name = name