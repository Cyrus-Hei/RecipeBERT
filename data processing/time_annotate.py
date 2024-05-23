import json
import re
import pandas
# tags: {0:untagged, 1:food_start, 2:food_linked, 3:time, 4:time_unit, 5:cooking methods, 6:measurement_value, 7:measurement}

default_puncs = [",",";",".",":"]
tag_food = []
tag_all = []
tag_time = []

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def iso_punc(sentence):
    for p in [", ","; ",". ",": "," (",") "]:
        sentence = sentence.replace(p, f" {p.strip()} ")
        sentence = sentence.replace('  ', ' ')
    if sentence[-1] == '.':
        sentence = sentence[:-1]+' .'
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


def time_tagger(txt):
    units = ["hour", "seconds", "minute"]
    ex_list = ['for', 'half', 'another', 'last', 'every', 'of', 'few',
               'couple', 'several', 'each', 'first']
    sent_split = txt.split()
    tags = []
    t_switch = False
    print(sent_split)
    for i in range(len(sent_split)):
        for u in units:
            if u in sent_split[i]:
                if sent_split[i-1] == 'more' or sent_split[i-1] == 'additional' or sent_split[i-1] == 'full':
                    if sent_split[i-2] == 'or':
                        tags[-3] = 3
                    else:
                        if is_number(sent_split[i-2]):
                            tags[-2] = 3
                            
                        # try:
                        #     float(sent_split[i-2])
                        #     tags[-2] = 3
                        # except:
                        #     pass
                # elif (sent_split[i-1] != 'last' and sent_split[i-1] != 'every' and 
                #       sent_split[i-1] != 'of' and sent_split[i-1] != 'few' and
                #       sent_split[i-1] != 'couple' and sent_split[i-1] != 'several' and
                #       sent_split[i-1] != 'each'):
                # elif sent_split[i-1] not in ex_list:
                #     tags[-1] = 3
                else:
                    if is_number(sent_split[i-1]):
                        tags[-1] = 3
                    # try:
                    #     float(sent_split[i-1])
                    #     tags[-1] = 3
                    # except:
                    #     pass
                tags.append(4)
                t_switch = True
                break
        if not t_switch:
            tags.append(0)
        else:
            t_switch = False
    return tags

def fracparsesent(sent):
    # print(sent)
    sent = sent.replace("°", " degrees")
    sent = sent.replace("half an hour", "30 minutes")
    sent = sent.replace("Half an hour", "30 minutes")
    sent = sent.replace("an hour", "1 hour")
    sent = sent.replace("An hour", "1 hour")
    sent = sent.replace("a hour", "1 hour")
    sent = sent.replace("A hour", "1 hour")
    sent = sent.replace("a minute", "1 minute")
    sent = sent.replace("A minute", "1 minute")
    sent = sent.replace("half a minute", "30 seconds")
    sent = sent.replace("Half a minute", "30 seconds")
    
    sent = sent.replace(" one ", " 1 ")
    sent = sent.replace("One ", "1 ")
    sent = sent.replace(" two ", " 2 ")
    sent = sent.replace("Two ", "2 ")
    sent = sent.replace(" three ", " 3 ")
    sent = sent.replace("Three ", "3 ")
    sent = sent.replace(" four ", " 4 ")
    sent = sent.replace("Four ", "4 ")
    sent = sent.replace(" five ", " 5 ")
    sent = sent.replace("Five ", "5 ")
    sent = sent.replace(" six ", " 6 ")
    sent = sent.replace("Six ", "6 ")
    sent = sent.replace(" seven ", " 7 ")
    sent = sent.replace("Seven ", "7 ")
    sent = sent.replace(" eight ", " 8 ")
    sent = sent.replace("Eight ", "8 ")
    sent = sent.replace(" nine ", " 9 ")
    sent = sent.replace("Nine ", "9 ")
    sent = sent.replace(" ten ", " 10 ")
    sent = sent.replace("Ten ", "10 ")
    sent = sent.replace(" twenty ", " 20 ")
    sent = sent.replace("Twenty ", "20 ")
    sent = sent.replace(" thirty ", " 30 ")
    sent = sent.replace("Thirty ", "30 ")
    sent = sent.replace(" forty ", " 40 ")
    sent = sent.replace("Forty ", "40 ")
    sent = sent.replace(" fifty ", " 50 ")
    sent = sent.replace("Fifty ", "50 ")
    sent = sent.replace(" sixty ", " 60 ")
    sent = sent.replace("Sixty ", "60 ")
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
        
    hyphened_num = re.findall('\d-\d', sent)
    for h in hyphened_num:
        sent = sent.replace(h, ' to '.join(h.split('-')))
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
    ssplit = sent.split()
    if 'to' in ssplit:
        count = ssplit.count('to')
        for i in range(count):
            to_ind = ssplit.index('to')
            try:
                val = f"{round((int(ssplit[to_ind-1])+int(ssplit[to_ind+1]))/2, 2):g}"
                ssplit = ssplit[:to_ind-1]+[str(val)]+ssplit[to_ind+2:]
            except:
                continue
        sent = " ".join(ssplit)
    return sent


samples = None
samples_corrected = []
with open("sentence100000.json","r") as f:
    samples = json.load(f)
    samples = [s[0] for s in samples]
    for i in range(len(samples)):
        samples[i] = iso_punc(samples[i])
        samples[i] = samples[i].replace("  ", " ")
        samples[i] = samples[i].replace("\t", " ")
    samples = [fracparsesent(s) for s in samples]
    count = 0
    for s in samples:
        temp_s = s
        
        
            
        # print('-'*70)
        # print(s)
        # print('*'*70)
        s = fix_punc(s)
        # print(s)
        # if "{" in temp_s:
        samples_corrected.append(s)
        tag_time.append(time_tagger(s))
samples_with_tags = [samples_corrected, tag_time]
df = pandas.DataFrame()
df['samples'] = samples_corrected
df['tag'] = tag_time
df.to_csv('bert/time-anno-100000.csv', index=False)
with open("time-anno-100000.json", "w") as f:
    json.dump(samples_with_tags, f , indent=1)