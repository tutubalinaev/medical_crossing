import os
import re

dir_1 = "Task1TrainSetGOLD200pipe/"
dir_2 = "TrainSetCorpus200EvaluationWorkbench/"

re_slesh_del = re.compile("\|+")
re_spacec_del = re.compile("[ ]+")
re_nl_del = re.compile("[\n]+")

dict_list = []
for file in os.listdir(dir_1):
    with open(dir_1 + file) as f:
        data = f.read().split("\n")
        for i in data:
            parsed = i.split("||")
            if len(parsed) == 5:
                dict_list.append({"txt_name": parsed[0], "type": parsed[1], "cui": parsed[2], "bounds": [(int(x),int(y)) for x,y in zip(parsed[3::2], parsed[4::2])]})
            #txt_name, type, cui, bounds = i.split("||")
            else:
                continue
                #dict_list.append({"txt_name": txt_name, "type":type, "cui":cui, "bounds": bounds})


for dict in dict_list:
    biosyn_format = ''
    with open(dir_2+dict['txt_name']) as f:
        data = f.read()
        if dict['cui'] == "CUI-less":
            continue
        for start, stop in dict["bounds"]:
            if stop - start == 1:
                stop += 1
            mention = data[start:stop].replace("\n", " ")
            left_ctx_bound = data[:start].rfind(".")
            left_ctx = data[left_ctx_bound+1:start]
            left_ctx = re.sub(re_slesh_del, " ", left_ctx)
            left_ctx = re.sub(re_spacec_del, " ", left_ctx)
            left_ctx = re.sub(re_nl_del, " ", left_ctx)
            right_ctx_bound = data[stop:].find(".")
            print(right_ctx_bound, data[stop:stop + 25])
            right_ctx = data[stop:stop + right_ctx_bound]
            right_ctx = re.sub(re_slesh_del, " ", right_ctx)
            right_ctx = re.sub(re_nl_del, " ", right_ctx)
            right_ctx = re.sub(re_spacec_del, " ", right_ctx)
            biosyn_format = f"{dict['txt_name']}||{start}|{stop}||{dict['type']}||{mention}||{dict['cui']}||{left_ctx}||{right_ctx}"
    filename = dir_2+dict['txt_name'].replace("txt", "concept")
    if os.path.exists(filename):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not
    with open(filename, append_write) as f:
        f.write(biosyn_format +"\n")

#with open("dataset.concept", 'w') as f:
#    f.write("\n".join(biosyn_format))
#print("\n".join(biosyn_format))
