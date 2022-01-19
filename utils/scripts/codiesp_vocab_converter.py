# coding: utf-8

import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="codiesp_codes/codiesp-D_codes.tsv")
    parser.add_argument("--output_es", default="data/vocabs/codiesp-d-codes-es.txt")
    parser.add_argument("--output_en", default="data/vocabs/codiesp-d-codes-en.txt")
    # parser.add_argument("--icd10_mapping_file", default="data/vocabs/ICD10CM-all-mapping.txt")
    args = parser.parse_args()

    # icd_map = {s.split("|")[1].strip(): s.split("|")[0] for s in open(args.icd10_mapping_file)}

    w_en = open(args.output_en, "w", encoding="utf-8")
    w_es = open(args.output_es, "w", encoding="utf-8")

    with open(args.file, "r", encoding="utf-8") as rf:
        for line in rf:
            try:
                code, spanish_name, english_name = line.split("\t")
                w_es.write(code); w_en.write(code)
                w_es.write("||"); w_en.write("||")
                w_es.write(spanish_name.lower()); w_en.write(english_name.strip().lower())
                w_es.write("\n"); w_en.write("\n")
            except Exception as e:
                print(e)

    w_en.close()
    w_es.close()