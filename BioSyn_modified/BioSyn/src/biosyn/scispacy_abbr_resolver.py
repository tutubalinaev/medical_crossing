# coding: utf-8

import spacy
from biosyn import Abbr_resolver

from scispacy.abbreviation import AbbreviationDetector


class SciSpacyAbbrResolver(Abbr_resolver):
    """
        Detects abbreviations using the algorithm in "A simple algorithm for identifying
        abbreviation definitions in biomedical text.", (Schwartz & Hearst, 2003).

        Note: OLDER than Ab3P (2008)!
    """

    def __init__(self):
        super().__init__(ab3p_path=None)
        self.nlp = spacy.load("en_core_sci_sm")
        self.nlp.add_pipe("abbreviation_detector")

    def resolve(self, corpus_path: str):

        result = {}

        with open(corpus_path, "r+", encoding="utf-8") as rf:
            for line in rf:
                doc = self.nlp(line.strip())
                for abrv in doc._.abbreviations:
                    result[str(abrv._.long_form)] = str(abrv)

        return result
