# coding: utf-8
from .base_parser import BaseOutputParser
# from base_parser import BaseOutputParser
import re


class FairEvalOutputParser(BaseOutputParser):

    def __init__(self, directory: str, stdout_filename="stdout.txt"):
        super().__init__(directory, stdout_filename)
        self.acc1_pattern = re.compile("Acc@1 is\s*(\S*)")
        self.acc5_pattern = re.compile("Acc@5 is\s*(\S*)")


if __name__ == "__main__":
    parser = FairEvalOutputParser("test_data", "fair_eval_example.txt")
    print(parser.read_scores())
