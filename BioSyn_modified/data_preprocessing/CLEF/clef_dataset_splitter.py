from random import shuffle
from math import ceil
import os
concepts = []

OUTPUT_DIR = "clef/"

if os.path.exists(OUTPUT_DIR) == False:
    os.mkdir(OUTPUT_DIR)
        
with open("dataset.concept") as f:
    concepts = f.read().split("\n")

dic = {}
with open("dictionary_processed.txt") as f:
    for line in f:
        k,v = line.strip().split("||")
        dic[k] = v
        
sets = {
    "train": ceil(0.5 * len(concepts)),
    "test" : ceil(0.25 * len(concepts)),
    "dev" : len(concepts) - ceil(0.25 * len(concepts)) - ceil(0.5 * len(concepts))
}


for set_, part in sets.items():
    shuffle(concepts)
    current_set = concepts[:part]
    print("Amount of concepts", len(concepts[:part]))
    concept_to_write = []
    dict_to_write = []
    for concept in current_set:
        id_ = concept.split("||")[4]
        if  id_ in dic.keys():
                concept_to_write.append(concept)
                dict_to_write.append(id_+"||"+dic[id_])
    dict_to_write = list(set(dict_to_write))
    print("Dict", len(dict_to_write))
    if os.path.exists(OUTPUT_DIR + set_) == False :
        os.mkdir(OUTPUT_DIR + set_)
    with open(OUTPUT_DIR + set_ + '/'+ set_+".concept", 'w') as f:
        f.write('\n'.join(concept_to_write))
    with open(OUTPUT_DIR + set_+"_dictionary"+".txt", 'w') as f:
        f.write('\n'.join(dict_to_write))
    concepts = concepts[part:]
    
    
    
    
    
