import json
import nltk
import inflect
import string

sg = inflect.engine()
def singularise(fname):
    with open(fname, "r") as f:
        ingr = json.load(f)
        new_ingr = {}
        for k in ingr.keys():
            new_k = xpunc(k.lower())
            new_ingr[new_k] = list(dict.fromkeys([" ".join(sg.singular_noun(j) or j for j in i.split()) for i in ingr[k]]))
        return(new_ingr)
    
def xpunc(text):
    ptext = [c for c in text if c not in string.punctuation]
    return ''.join(ptext)
        
if __name__ == '__main__':
    fname = input("file name: ")
    try:
        with open(fname, "r") as f:
            rcp = json.load(f)
    except Exception:
        print("error")
        exit()
    singr = singularise(fname)
    ofname = "singed-"+fname
    with open(ofname, "w") as f:
        json.dump(singr, f, indent=2)
    print(singr)