# coding:utf-8
from argparse import ArgumentParser


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('--umls_root', default="../../",
                        help="Path to the MRCONSO and MRSTY", type=str)
    parser.add_argument('--result_file', default="../../SNOMEDCT_US_clef2013-unaggregated.txt",
                        help="Path to the unaggregated SNOMEDCT_US dictionary filtered for clef2013", type=str)

    args = parser.parse_args()
    print(args)

    ROOT = args.umls_root
    all_cuis = set([line.split("|")[0] for line in open(ROOT + "MRSTY_DISO.RRF", "r+", encoding="utf-8")])

    print("MRSTY lines of interest to us:", len(all_cuis))

    all_data = [(line.split("|")[0], line.split("|")[14])
                for line in open(ROOT + "MRCONSO.RRF", "r+", encoding="utf-8")
                if "|SNOMEDCT_US|" in line and line.split("|")[0] in all_cuis]

    print("MRCONSO lines of interest to us:", len(all_data))

    with open(args.result_file, "w+", encoding="utf-8") as wf:
        for cui, name in all_data:
            wf.write(cui)
            wf.write("||")
            wf.write(name)
            wf.write("\n")