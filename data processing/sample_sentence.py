import json
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from nltk.tokenize import sent_tokenize
import re

tokenizer = AutoTokenizer.from_pretrained("Dizex/InstaFoodRoBERTa-NER")
model = AutoModelForTokenClassification.from_pretrained("Dizex/InstaFoodRoBERTa-NER")

pipe = pipeline("ner", model=model, tokenizer=tokenizer)
example = "Today's meal: Fresh olive poké bowl topped with chia seeds. Very delicious!"

ner_entity_results = pipe(example, aggregation_strategy="simple")
# temp = []
# for i in range(len(ner_entity_results)):
#     start = ner_entity_results[i]["start"]
#     end = ner_entity_results[i]["end"]
#     if i != 0:
#         if start == ner_entity_results[i-1]["end"]:
#             last = temp[-1]
#             temp.remove(last)
#             temp.append((last[0],end))
#         else:
#             temp.append((start, end))
#     else:
#             temp.append((start, end))

def get_food_indices(ner_result):
    ents = []
    for ent in ner_result:
        e = {"start": ent["start"], "end": ent["end"], "label": ent["entity_group"]}
        if ents and -1 <= ent["start"] - ents[-1]["end"] <= 1 and ents[-1]["label"] == e["label"]:
            ents[-1]["end"] = e["end"]
            continue
        ents.append(e)
    return(ents)

steps = []
with open("sentence100000.json", "r") as f:
    rcp = json.load(f)
    # rcp = rcp[:10]
    if isinstance(rcp[0], dict):
        for r in rcp:
            for s in r["steps"]:
                steps.extend(sent_tokenize(s))
    else:
        steps = [s[0] for s in rcp]

puncs = [",", ";", "."]
samples = []
for s in steps:
    # print(s)
    tag_id = []
    new_s = ""
    current_ind = 0
    ner_entity_results = pipe(s, aggregation_strategy="simple")
    food_indices = get_food_indices(ner_entity_results)
    # print(food_indices)
    # print(s)
    for i in food_indices:
        # print(i["start"],i["end"])
        tag_id.extend([0 for w in s[current_ind:i["start"]].split() if w not in puncs])
        # print(s[current_ind:i["start"]].split())
        # print(s[i["start"]:i["end"]])
        tag_id.extend([1 if i == 0 else 2 for i in range(len(s[i["start"]:i["end"]].split()))])
        new_s += s[current_ind:i["start"]] + "{"+s[i["start"]:i["end"]]+"}"
        # new_s += s[current_ind:i["start"]] + "{}"
        current_ind = i["end"]
    if current_ind != len(s):
        tag_id.extend([0 for w in s[current_ind:].split() if w not in puncs])
        # print(s[current_ind:].split())
        new_s += s[current_ind:]
    # print(new_s)
    samples.append([new_s, tag_id])

samples = [s for s in samples if re.search("{", s[0])]


with open("annotated-samples-100000.json", "w") as f:
    json.dump(samples, f , indent=2)
# print(len(steps))
