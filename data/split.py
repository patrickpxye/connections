import random
import json
import math

with open("connections.json", "rb") as f:
    data = list(json.load(f).values())

random.shuffle(data)
n = len(data)
train_split = math.ceil(n * 0.8)
val_split = math.ceil(n * 0.9)
train_data = data[:train_split]
print("training data of length ", train_split)  # 274
val_data = data[train_split:val_split]
print("val data of length ", val_split - train_split)  # 34
test_data = data[val_split:]
print("test data of split ", n - val_split)  # 34


with open("splits/connections_train.json", "w") as f:
    json.dump(train_data, f, indent=4)

with open("splits/connections_val.json", "w") as f:
    json.dump(val_data, f, indent=4)

with open("splits/connections_test.json", "w") as f:
    json.dump(test_data, f, indent=4)
