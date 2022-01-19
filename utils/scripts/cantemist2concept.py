# coding: utf-8
"""
    DESIRED:
    N000||232|244||Entity||hiv positive||C0019699||||

    AVAILABLE:
    T1	MORFOLOGIA_NEOPLASIA 2716 2742	Adenocarcinoma infiltrante
    #1	AnnotatorNotes T1	8140/3/H
    T2	MORFOLOGIA_NEOPLASIA 2784 2801	células tumorales
"""
import os

if __name__ == "__main__":

    sets = ["train-set", "test-set"]

    for data_segment_name in sets:

        dataset = f"data/datasets/cantemist/{data_segment_name}/cantemist-norm"

        try:
            os.mkdir(dataset + "-concepts")
        except Exception as e:
            print(e)

        for f in os.listdir(dataset):

            if not f.endswith("ann"):
                continue

            new_name = f.replace(".ann", ".concept")
            t_id = None

            with open(dataset + "-concepts/" + new_name, "w+", encoding="utf-8") as wf:

                for line in open(dataset + "/" + f, encoding="utf-8"):

                    if line.startswith("T"):
                        row = line.strip().split("\t")
                        t_id = row[0]
                        str_id = "N%03d" % int(t_id.replace("T", ""))
                        _, fromm, too = row[1].split(" ")
                        fromm, too = int(fromm), int(too)
                        wf.write(f"{str_id}||{fromm}|{too}||Entity||{row[2]}||")

                    elif line.startswith("#"):

                        row = line.strip().split("\t")
                        current_t_id = row[1].split(" ")[-1]
                        assert current_t_id == t_id
                        wf.write(row[2])
                        wf.write("||||\n")
