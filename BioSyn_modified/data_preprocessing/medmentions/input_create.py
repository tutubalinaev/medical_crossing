"""
This file is used to convert Mad Mentions ST21pv dataset (https://github.com/chanzuckerberg/MedMentions/tree/master/st21pv)
to BioSyn input format
"""
import csv

ontologies = ["CPT","FMA","GO",
              "HGNC","HPO","ICD10",
              "ICD10CM","ICD9CM","MDR",
              "MSH","MTH","NCBI",
              "NCI","NDDF","NDFRT",
              "OMIM","RXNORM","SNOMEDCT_US"]

path_types = "SemGroups.txt"
with open(path_types) as f:
    reader = csv.reader(f, delimiter="|")
    raw_types = list(reader)

sem_groups = {}
for line in raw_types:
    sem_groups[line[2]] = line[0]

path_data = "corpus_pubtator_st21pv.txt"
with open(path_data) as f:
    reader = csv.reader(f, delimiter="\t")
    raw_mm = list(reader)

cuids = []

bs_mm = []
text = ""
flag = True
true_counter = 0
for i, meta in enumerate(raw_mm):
    flag = True
    # if the string is not abstract
    if len(meta)>1:
        flag = False

        doc_id = meta[0]
        start = meta[1]
        end = meta[2]
        name = meta[3]
        try:
            cuid = meta[5][5:]
        except:
            print(meta)
            pass
        left_context = text[:int(start,10)]
        right_context = text[int(end, 10):]

        cuids.append(cuid)

        if ',' in meta[4]:  # some lines contain double types, e.g. "T116,T123"
            types = meta[4].split(',')
            for t in types:
                try:
                    type = sem_groups[t]
                except KeyError:
                    continue
                line = doc_id + "||" + start + "|" + end + "||" + type + "||" + name + "||" + cuid + "||" + left_context + "||" + right_context
                bs_mm.append(line)
        else:
            try:
                type = sem_groups[meta[4]]
            except KeyError:
                continue
            line = doc_id+"||"+start+"|"+end+"||"+type+"||"+name+"||"+cuid  + "||" + left_context + "||" + right_context
            bs_mm.append(line)
    
    elif flag:
        if true_counter > 1:
            text = ""
            true_counter = 0
        if true_counter == 1:
            text += meta[0].split("|a|")[-1]
        else:
            try:
                text += meta[0].split("|t|")[-1] + " "
            except IndexError:
                print(meta)
                print("{}/{}".format(i, len(raw_mm)))
                continue
        true_counter += 1
    #print("{}/{}".format(i, len(raw_mm)))

bs_mm = list(set(bs_mm))
with open('mm_st21pv_input.concept','w') as f:
    f.write('\n'.join(bs_mm))
