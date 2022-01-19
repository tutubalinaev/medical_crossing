"""
This script was used to create train-test-dev split of preprocessed filtered by semantic type MedMentions st21pv dataset
"""

with open("corpus_pubtator_pmids_dev.txt") as f:
    id_dev = f.readlines()

with open("corpus_pubtator_pmids_test.txt") as f:
    id_test = f.readlines()

with open("corpus_pubtator_pmids_trng.txt") as f:
    id_train = f.readlines()

with open("mm_st21pv_input_prep_DISO.concept") as f: 
    data = f.readlines()

id_dev = [el[:-1] for el in id_dev]
id_test = [el[:-1] for el in id_test]
id_train = [el[:-1] for el in id_train]

dev=[]
test=[]
train=[]
train_ents = []

for i in range(len(data)):
    els = data[i].split("||")
    if els[0] in id_train:
        train.append(data[i])
        train_ents.append(els[-4])

for i in range(len(data)):
    els = data[i].split("||")
    if els[0] in id_test:
        if els[-4] not in train_ents:
            test.append(data[i])
        else:
            continue
    elif els[0] in id_dev:
        if els[-4] not in train_ents:
            dev.append(data[i])
        else:
            continue
    else:
        continue


with open("mm_st21pv_input_prep_DISO_train.concept", 'w') as f:
    f.write(''.join(train))

with open("mm_st21pv_input_prep_DISO_test.concept", 'w') as f:
    f.write(''.join(test))

with open("mm_st21pv_input_prep_DISO_dev.concept", 'w') as f:
    f.write(''.join(dev))
