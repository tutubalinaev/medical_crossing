# coding: utf-8

with open("data/vocabs/CANTEMIST-lopez-ubeda-et-al.txt", "w", encoding="utf-8") as wf:
    for line in open("cieo-synonyms.csv", "r", encoding="utf-8"):
        splitted = line.strip().split("\t")
        wf.write(splitted[0] + "||" + splitted[1].lower() + "\n")
