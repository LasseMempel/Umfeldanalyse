import requests
import pandas as pd

link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRn7-bEMXaFl5KXDok508vQFS95PzWddFYYjJbhlhx8ARBgzPJg8nYAeOgCOVwFaQ/pub?output=csv"
response = requests.get(link)

# load response csv as pd df
df = pd.read_csv(link)
# print first 5 rows
#print(df.head())

def check_url(url):
    s = requests.session()
    s.max_redirects = 100
    print(f"Checking {url}")
    try:
        response = s.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        # if error = requests.exceptions.TooManyRedirects, return True
        if isinstance(e, requests.exceptions.TooManyRedirects):
            print(f"Too many redirects for {url}")
            return True
        else:
            print(f"Error: {e}")
            return False
    
# check all urls in column "Website"
# create new column "Responsive"
df["Responsive"] = df["Website"].apply(lambda x: check_url(x) if isinstance(x, str) else False)
# save df to csv
df = df.replace(r'\n', '', regex=True)
df.to_csv("Umfeldanalyse.csv", index=False)

"""
Weitere Ideen: 
- aktuell/gepflegt
- Open access
- Lizenz
- Software / Modell / Format
- Sprache
- Land
- Fachbereich / Material (aufteilen in Kurz Beschreibung und Schlagworten, danach löschen)
- Themen (aufteilen in Kurz Beschreibung und Schlagworten, danach löschen)
- Schlagworte
- Kurz Beschreibung
- Kategorie (Ontologie, Vokabular, Datenschema, Fachtext, Datenbank)
- Institution
"""