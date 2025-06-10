import spacy
import pandas as pd
import json

nlp = spacy.load("de_dep_news_trf")
table = pd.read_csv("/home/lasse/repos/Umfeldanalyse/Umfeldanalyse-Arbeitstabelle.csv", sep=",")

schlagwortDict = {}

"""
for i, row in table.iterrows():
    schlagworte = row["Schlagworte"]
    if pd.isna(schlagworte):
        continue
    doc = nlp(schlagworte)
    for token in doc:
        if token.pos_ == "NOUN":
            if token.lemma_ != token.text:
                if token.lemma_ not in schlagwortDict:
                    schlagwortDict[token.text] = [token.lemma_]
with open("schlagwortDict.json", "w") as f:
    json.dump(schlagwortDict, f, ensure_ascii=False, indent=4)
"""
# replace the original Schlagworte with their singular forms

with open("schlagwortDict.json", "r") as f:
    schlagwortDict = json.load(f)

for i, row in table.iterrows():
    schlagworte = row["Schlagworte"]
    if pd.isna(schlagworte):
        continue
    schlagwörter = schlagworte.split(", ")
    schlagwörter = [x.strip() for x in schlagwörter]
    """
    for i in range(len(schlagwörter)):
        if schlagwörter[i] in schlagwortDict:
            schlagwörter[i] = schlagwortDict[schlagwörter[i]]
    """
    schlagwörter = [schlagwortDict[x][0] if x in schlagwortDict else x for x in schlagwörter]
    try:
        schlagwörter = ", ".join(schlagwörter)
    except:
        print(schlagwörter)
        raise TypeError
    table.at[i, "Schlagworte"] = schlagwörter
table.to_csv("/home/lasse/repos/Umfeldanalyse/Umfeldanalyse-Arbeitstabelle_singular.csv", sep=",", index=False)