import nltk
import pickle
import json
import string
import inflect
import re
nltk.download('stopwords')
nltk.download('wordnet')
lem = nltk.stem.WordNetLemmatizer()

ingr_exceptions = {"lemon grass": "lemongrass"}

def prep(filename):
    with open(filename, "r") as f:
        # rcp = pickle.load(f)
        rcp = json.load(f)
        for r in rcp:
            r['recipe'] = r['recipe'].lower()
            r['recipe'] = xpunc(r['recipe'])
            r['ingr'] = [[j.lower() for j in i]  for i in r['ingr']]
            for i in r['ingr']:
                if i[1] != "":
                    i[1] = fracparse(i[1])
            u_ingr = []
            for i in r['ingr']:
                if i[0] != "" and i[0] not in u_ingr and i[0] not in ingr_exceptions:
                    u_ingr.append(i[0])
                elif i[0] in list(ingr_exceptions.keys()):
                    u_ingr.append(ingr_exceptions[i[0]])
            sg = inflect.engine()
            u_ingr = [" ".join(sg.singular_noun(j) or j for j in i.split()) for i in u_ingr]
            # u_ingr = list(map(lambda x: x.replace('lemongras', 'lemongrass') and x.replace('asparagu', 'asparagus'), u_ingr))
            for i in range(len(u_ingr)):
                if u_ingr[i] == "asparagu":
                    u_ingr[i] = "asparagus"
                elif u_ingr[i] == "lemongras":
                    u_ingr[i] = "lemongrass"
            r['unique_ingr'] = u_ingr
            # r['unique_ingr'] = [u_ingr.append(i[0]) for i in r['ingr'] if i[0] not in u_ingr]
            stopword = nltk.corpus.stopwords.words('english')
            r['steps'] = [xpunc(s.lower()).split() for s in r['steps']]
            r['steps'] = [[lem.lemmatize(w) for w in s if w not in stopword or w =="all"] for s in r['steps']]
            for k, e in ingr_exceptions.items():
                temp_steps = []
                for s in r["steps"]:
                    print(s)
                    temp_steps.append(" ".join(s).replace(k, e).split())
                r["steps"] = temp_steps
                
            r['allsteps'] = [w for s in r['steps'] for w in s]
            # for s in r['steps']:
            #     s = s.lower()
            
        return rcp
    
def xpunc(text):
    ptext = [c for c in text if c not in string.punctuation]
    return ''.join(ptext)
    
    
def fracparse(text):
    frac = 0
    if re.search("[a-zA-Z]+", text):
        return frac
    
    if " " in text:
        text = text.split(" ")
        frac += int(text[0])
        text = text[1]
    
    if "/" in text:
        text = text.split("/")
        frac += int(text[0])/int(text[1])
        text = 0
        
    frac += int(text)
    
    return frac

if __name__ == '__main__':
    # print(fracparse(input("number: ")))
    # print(xpunc(input("text: ")))
    # print(lem.lemmatize("wants"))
    fname = input("file name: ")
    try:
        with open(fname, "r") as f:
            rcp = json.load(f)
    except Exception:
        print("error")
        exit()
            
    
    prcp = prep(fname)
    with open(f"p-{fname}", "w") as f:
        json.dump(prcp, f, indent = 2)
        print("saved")
    print(prcp)
    
    
