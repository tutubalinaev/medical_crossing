# coding: utf-8
import os
import re


class ResultsBundle(object):

    def __init__(self, acc1: float = None, acc5: float = None):
        self.acc1, self.acc5 = acc1, acc5

    def get_acc1(self):
        return self.acc1

    def get_acc5(self):
        return self.acc5

    def __repr__(self) -> str:
        return "Results(Acc@1=%.4f, Acc@5=%.4f)" % (self.acc1, self.acc5)

    def to_dict(self) -> dict:
        return {"acc1": self.acc1, "acc5": self.acc5}

    def is_empty(self) -> bool:
        return self.acc5 is None and self.acc1 is None


class BaseOutputParser(object):
    """
        Works with BioSyn and SapBert
    """

    def __init__(self, directory: str, stdout_filename="stdout.txt", name="default"):
        self.directory = directory
        self.stdout_filename = stdout_filename
        self.acc1_pattern = re.compile("acc@1=(\S*)")
        self.acc5_pattern = re.compile("acc@5=(\S*)")
        self.name = name
        # todo: read all the necessary parameters from YAML files
        pass

    def read_scores(self):
        acc1, acc5 = None, None
        try:
            for line in open(os.path.join(self.directory, self.stdout_filename), "r", encoding="utf-8"):
                line = line.strip()
                acc1s, acc5s = self.acc1_pattern.findall(line), self.acc5_pattern.findall(line)
                if len(acc1s) > 0:
                    # print(acc1s)
                    acc1 = float(acc1s[0])
                if len(acc5s) > 0:
                    # print(acc5s)
                    acc5 = float(acc5s[0])
        except Exception as e:
            # todo: say something smart and encouraging?
            raise e

        return ResultsBundle(acc1=acc1, acc5=acc5)


if __name__ == "__main__":
    # test
    parser = BaseOutputParser("test_data/", stdout_filename="stdout.txt")
    print(parser.read_scores())
