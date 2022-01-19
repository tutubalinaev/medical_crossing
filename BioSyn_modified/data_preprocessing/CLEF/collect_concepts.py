import os

data = []

for fl in os.listdir("processed"):
    with open("processed/"+fl) as f:
        data.extend(f.read().strip().split('\n'))
with open("dataset.concept", 'w') as f:
    f.write("\n".join(data))
