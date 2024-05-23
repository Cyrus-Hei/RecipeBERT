import json
import re
# tags: {0:untagged, 1:food_start, 2:food_linked, 3:time, 4:time_unit, 5:cooking methods, 6:measurement_value, 7:measurement}

default_puncs = [",",";",".",":"]
tag_food = []
tag_all = []
tag_time = []

def iso_punc(sentence):
    for p in [", ","; ",". ",": "," (",") "]:
        sentence = sentence.replace(p, f" {p.strip()} ")
        sentence = sentence.replace('  ', ' ')
    if sentence[-1] == '.':
        sentence = sentence[:-1]+' .'
    # for p in [") "]:
    #     sentence = sentence.replace(p, f" {p.strip()} ")
    #     sentence = sentence.replace('  ', ' ')
    return sentence.strip()

def fix_punc(sentence):
    for p in [" , "," ; "," . "," : "," ) "]:
        sentence = sentence.replace(p, p[1:])
    for p in [" ( "]:
        sentence = sentence.replace(p, p[:-1])
    if sentence[-2:] == ' .':
        sentence = sentence[:-2]+'.'
    return sentence

def xpunc(text, puncs):
    ptext = [c for c in text if c not in puncs]
    return ''.join(ptext)

def food_tagger(txt):
    sent_split= txt.split()
    ret = []
    food_switch = False
    for s in sent_split:
        if "{" in s and "}" in s:
            ret.append(1)
        elif "{" in s:
            ret.append(1)
            food_switch = True
        elif food_switch == True:
            ret.append(2)
            if "}" in s:
                food_switch = False
        else:
            ret.append(0)
    return(ret)

def time_tagger(txt):
    tags = []
    units = ["hour", "second", "minute"]
    sent_split = txt.split()
    t_switch = False
    for i in range(len(sent_split)):
        for u in units:
            if u in sent_split[i]:
                tags[-1] = 3
                tags.append(4)
                t_switch = True
                break
        if not t_switch:
            tags.append(0)
        else:
            t_switch = False
    return tags

def fracparsesent(sent):
    print(sent)
    sent = sent.replace("°", " degrees")
    inch = re.findall("\d+\"", sent)
    for i in range(len(inch)):
        if int(inch[i][:-1]) == 1:
            sent = sent.replace(inch[i], inch[i][:-1]+" inch")
        else:
            sent = sent.replace(inch[i], inch[i][:-1]+" inches")
    backsl = re.findall("\d\\\\\d", sent)
    for i in range(len(backsl)):
        sent = sent.replace(backsl[i], "/".join(backsl[0].split("\\")))
    if " /" in sent:
        sent = sent.replace(" /", "/")
    if " - " in sent:
        sent = sent.replace(" - ", "-")
    if " -" in sent:
        sent = sent.replace(" -", "-")
    # if re.findall("\d-\d", sent):
    #     print(sent)
    #     for r in re.findall("\d-\d", sent):
    #         r_split = r.split("-")
    #         sent = sent.replace(r, r_split[0]+" to "+r_split[1])
    #     print(sent)
    ssplit = sent.split()
    i = 0
    # print(ssplit)
    while i < len(ssplit):
        if re.match(".*\d.*", ssplit[i]):
            frac = 0
            temp_w = xpunc(ssplit[i],[",",";",".",":","(",")"]).split("-")[0]
            if re.search("[0-9]+\.[0-9]+", temp_w) or re.search("[a-zA-Z]+", temp_w):
                i += 1
            elif temp_w.isdigit():
                frac += int(temp_w)
                if i+1 < len(ssplit):
                    if re.match(".*\d.*", ssplit[i+1]):
                        temp_w2 = xpunc(ssplit[i+1],[",",";",".",":","(",")"]).split("-")[0]
                        if re.search("[a-zA-Z]+", temp_w2):
                            i += 1
                        elif temp_w2.isdigit():
                            i += 1
                        elif "%" in temp_w2:
                            i += 1
                        else:
                            frac_split = temp_w2.split("/")
                            frac += int(frac_split[0])/int(frac_split[1])
                            sent = sent.replace(temp_w+" "+temp_w2, f"{round(frac,2):g}")
                            i += 2
                    else:
                        i += 1
                else:
                    i += 1
            elif "/" in temp_w:
                frac_split = temp_w.split("/")
                frac += int(frac_split[0])/int(frac_split[1])
                sent = sent.replace(temp_w, f"{round(frac,2):g}")
                i += 1
            else:
                i += 1
        else:
            i += 1
    # Turn "x to y" into the mean of x and y
    ssplit = sent[-1].split()
    if 'to' in ssplit:
        count = ssplit.count('to')
        for i in range(count):
            to_ind = ssplit.index('to')
            val = f"{round((int(ssplit[to_ind-1])+int(ssplit[to_ind+1]))/2, 2):g}"
            ssplit = ssplit[:to_ind-1]+[str(val)]+ssplit[to_ind+2:]
        sent = " ".join(ssplit)
    # if "to" in sent:
    #     n = 0
    #     print(sent)
    #     while n < len(sent):
    #         try:
    #             if sent[sent.index("to", n)-2].isdigit() and sent[sent.index("to", n)+3].isdigit():
    #                 j = 2
    #                 k = 3
    #                 while sent[sent.index("to", n)-j] != " " or sent[sent.index("to", n)+k] != " ":
    #                     if sent[sent.index("to", n)-j] != " ":
    #                         j += 1
    #                     if sent[sent.index("to", n)+k] != " ":
    #                         k += 1
    #                 to_split = [int(i) for i in sent[sent.index("to", n)-(j-1):sent.index("to", n)+k].split(" to ")]
    #                 new_val = f"{round((to_split[0]+to_split[1])/2, 2):g}"
    #                 sent = sent.replace(sent[sent.index("to", n)-(j-1):sent.index("to", n)+k], new_val)
    #                 # n = sent.index("to", n ) + k-1
    #             else:
    #                 n = sent.index("to", n ) + 3
    #         except ValueError:
    #             # print("error")
    #             # print(sent[n:])
    #             break
    # print(sent)
    return sent

exclude_variants = []
for w in ["parchment", "wok", "shortening", "paper towel", "paper towels", "knead", "dust", "balls"]:
    exclude_variants.append(w)
    exclude_variants.append(w.upper())
    exclude_variants.append(w[0].upper()+w[1:])
    
exclude_compound = []
for w in  ["marinade", "mixture", "mix", "dough", "salad", "dressing", "and"]:
    exclude_compound.append(w)
    exclude_compound.append(w.upper())
    exclude_compound.append(w[0].upper()+w[1:])
print(exclude_variants)

samples = None
samples_corrected = []
with open("annotated-samples-100000.json","r") as f:
# with open("annotated-samples500.json","r") as f:
    samples = json.load(f)
    samples = [s[0] for s in samples]
    for i in range(len(samples)):
        samples[i] = iso_punc(samples[i])
        samples[i] = samples[i].replace("  ", " ")
        samples[i] = samples[i].replace("\t", " ")
        samples[i] = samples[i].replace("{ ", " {")
        samples[i] = " ".join([ss.replace('}', '')+'}' if '}' in ss and ss[-1] != '}' else ss for ss in samples[i].split()])
        # print([ss.replace('}', '')+'}' if '}' in ss and ss[-1] != '}' else ss for ss in samples[i].split()])
        # print('test: '," ".join([ss.replace('}', '')+'}' if '}' in ss and ss[-1] != '}' else ss for s in samples[i] for ss in s.split()]))
        open_curl = re.findall("{\d[^\s]+", samples[i])
        for m in open_curl:
            if '7up' in m.lower() or '7-up' in m.lower():
                continue
            if '}' in m:
                samples[i] = samples[i].replace(m, m.replace("{", '').replace('}', ''))
            else:
                samples[i] = samples[i].replace(m+" ", m[1:]+" {")
    samples = [fracparsesent(s) for s in samples]
    # samples = [s[0] for s in samples]
    
    # samples = ["Add the cooked {meatballs}, and simmer in the {tomato sauce} for 5 to 10 minutes 4 to 6 until completely cooked."]
    # samples = [fracparsesent(samples[0])]
    count = 0
    for s in samples:
        temp_s = s
        # temp_s = xpunc(s, default_puncs)
        
        if re.findall("\d-\d", temp_s):
            continue
        splits = s.split()
        # splits = xpunc(s,[",",";",".",":","(",")"]).split()
        i = 0
        while i < (len(splits)):
            if "{" in splits[i] and (splits[i][0] != "{" or splits[i].count("{") > 1):
                # print(splits[i])
                j = i+1
                while " ".join(splits[i:j]).count("{") > " ".join(splits[i:j]).count("}"):
                    j += 1
                wsplit = [w for w in re.split("[{},.!;]"," ".join(splits[i:j])) if w != ""]
                s = s.replace(" ".join(splits[i:j]), "{"+"".join(wsplit)+"}")
                # print(" ".join(splits[i:j]))
                # print("{"+"".join(wsplit)+"}")
                i = j
            else:
                i += 1
        
        # if len(s.split()) != len(s[1]):
        #     print(len(s.split()),len(s[1]))
        
        # temp_s = xpunc(s, default_puncs)
        
            
        for i in range(2):
            for w in exclude_compound:
                if "{"+w+"}" in temp_s:
                    s = s.replace("{"+w+"}", w)
                    # print("s1", s, temp_s)
                    # s[1][temp_s.split().index("{"+w+"}")] = 0
                elif w+"}" in temp_s:
                    # print(temp_s)
                    # print(s[s.find(w+"}")-2])
                    if s[s.find(w+"}")-2] != "}":
                        s = s[:s.find(w+"}")-1]+"}"+s[s.find(w+"}")-1:]
                    s = s.replace(w+"}", w)
                    # print("r2",s)
                    # s = s.replace(temp_s.split()[temp_s.split().index(w+"}")-1], temp_s.split()[temp_s.split().index(w+"}")-1]+"}")
                    
                    # print(temp_s.split()[temp_s.split().index(w+"}")-1], temp_s.split()[temp_s.split().index(w+"}")-1]+"}")
                    # s[1][temp_s.split().index(w+"}")] = 0
                # temp_s = xpunc(s, default_puncs)
            

        for w in exclude_variants:
            if f"{{{w}}}" in temp_s:
                # print(f"{{{w}}}")
                s = s.replace(f"{{{w}}}", w)
                # s[1][temp_s.split().index(f"{{{w}}}")] = 0
        # temp_s = xpunc(s, default_puncs)
        print('-'*70)
        print(s)
        print('*'*70)
        s = fix_punc(s)
        print(s)
        if "{" in temp_s:
            samples_corrected.append(s)
            tag_food.append(food_tagger(s))
            tag_time.append(time_tagger(s))
        # if re.findall("\d-\d", s) or re.findall("\d\s-\s\d", s):
        #     print(re.findall("\d-\d", s))
        #     print(re.findall("\d\s-\s\d", s))
        
        
        
        
        # food_match = re.findall("{.*}", s)
        
        # for fd in food_match:
        #     if len(fd) <= 4:
        #         print(fd)
            # temp_s.split()[temp_s.split().index("mixture}")-1]
            # continue
            # count +=1
            # print(s)
        # if len(s.split()) != len(s[1]):
        #     print(len(s.split()),len(s[1]))
        #     print(s[1])
    # print(samples)
# print(samples)
samples_with_tags = [samples_corrected, tag_food, tag_time, tag_all]
with open("annotated-samples-corrected-100000.json", "w") as f:
    json.dump(samples_with_tags, f , indent=1)