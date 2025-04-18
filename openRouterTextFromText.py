import requests
import html_text
from htmldate import find_date
import pandas as pd
import json
import time

# OpenRouter API endpoint and key
from config import API_KEY
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def generateTextFromText(payload):
    try:
        # Prepare the payload
        # Set up the headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        # Make the API request
        response = requests.post(API_URL, json=payload, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            return f"API Error: {response.status_code}, {response.text}"

    except requests.RequestException as e:
        return f"Request Error: {str(e)}"
    except IOError as e:
        return f"Image Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"
    
def generatePayload(model, prompt, context):
    structuredPayload = {
        "model": model,
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt + context
                }
            ]
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
            "name": "resource_metadata",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                "Lizenz": {
                    "type": "string",
                    "description": "Lizenz, unter der die Ressource veröffentlicht ist"
                },
                "Sprache": {
                    "type": "string",
                    "description": "Sprache der Ressource"
                },
                "Land": {
                    "type": "string",
                    "description": "Land, in dem die Ressource veröffentlicht wurde"
                },
                "Schlagworte": {
                    "type": "string",
                    "description": "Schlagworte, die die Ressource beschreiben. Getrennt durch Komma"
                },
                "Kurz Beschreibung": {
                    "type": "string",
                    "description": "Kurze Beschreibung der Ressource"
                },
                "Kategorie": {
                    "type": "string",
                    "enum": ["Ontologie", "Vokabular", "Datenschema", "Fachtext", "Datenbank"],
                    "description": "Kategorie der Ressource"
                },
                "Software / Modell / Format": {
                    "type": "string",
                    "description": "Format der Ressource (z.B. PDF, HTML, CSV, JSON, RDF, XML, OWL, MediaWiki). Mehrere Formate durch Komma getrennt"
                },
                "Open access": {
                    "type": "string",
                    "description": "Ist die Ressource offen verfügbar? X für ja, - für nein."
                },
                },
                "required": ["Lizenz", "Sprache", "Land", "Schlagworte", "Kurz Beschreibung", "Kategorie",  "Software / Modell / Format", "Open access"],
                "additionalProperties": False
            }
            }
        }
    }
    return structuredPayload


def generatePrompt(Ressource):
    prompt = f"""
    Ermittle unter Zuhilfenahme des folgenden Textes die aufgelisteten Informationen über die Ressource: {Ressource}.
    - Lizenz # Lizenz, unter der die Ressource veröffentlicht ist
    - Sprache  # Sprache der Ressource
    - Land # Land, in dem die Ressource veröffentlicht wurde
    - Schlagworte # Schlagworte, die die Ressource beschreiben, getrennt durch Komma
    - Kurz Beschreibung # kurze Beschreibung der Ressource
    - Kategorie # entweder Ontologie, Vokabular, Datenschema, Fachtext (wie z.B. ein Wiki) oder Datenbank
    - Software / Modell / Format  # Format der Ressource (z.B. PDF, HTML, JSON)
    - Open access # x für ja, - für nein. Ob die Ressource Open Access ist oder nicht

    Sind Informationen nicht explizit verfügbar, wähle als Wert einen leeren String "".

    Hier ist der Text:

    """
    return prompt

models = [
    "google/gemini-2.0-flash-exp:free",
    "google/gemini-2.5-pro-exp-03-25:free",
    "google/gemma-3-27b-it:free", 
    "deepseek/deepseek-r1-distill-llama-70b:free", 
    "nvidia/llama-3.1-nemotron-70b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "deepseek/deepseek-r1-distill-qwen-32b:free",
    "google/gemma-3-12b-it:free",
    "mistralai/mistral-nemo:free",
    "google/gemma-2-9b-it:free"
    # unused
    "deepseek/deepseek-chat-v3-0324:free",
    "google/gemini-2.5-pro-exp-03-25:free",
    "qwen/qwq-32b:free",
    "deepseek/deepseek-v3-base:free",
    "google/gemini-2.0-flash-thinking-exp-1219:free",
    "deepseek/deepseek-r1-zero:free",
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
    "nvidia/llama-3.3-nemotron-super-49b-v1:free",
    ]

if __name__ == "__main__":
    link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRn7-bEMXaFl5KXDok508vQFS95PzWddFYYjJbhlhx8ARBgzPJg8nYAeOgCOVwFaQ/pub?output=csv"
    response = requests.get(link)
    df = pd.read_csv(link)
    # reduce df to only 5 rows
    #df = df.head(1)
    df["Letzte Aktualisierung"] = ""
    optionalColumns = ["Software / Modell / Format", "Open access", "Lizenz", "Sprache", "Land", "Kategorie"]
    facultativeColumns = ["Kurz Beschreibung", "Schlagworte"]
    for index, row in df.iterrows():
        # reset context, website and additionalContext
        context = ""
        additionalContext = ""
        website = ""
        Name = row["Name"]
        Responsive = row["Responsive"]
        Kategorie = row["Kategorie"]
        if pd.isna(Name):
            print("Name is NaN")
            continue
        print(f"Working on {index}: {Name}" )
        print("\n")
        if Responsive:
            website = row["Website"]
            try:
                date = find_date(website)
                df.at[index, "Letzte Aktualisierung"] = date
            except:
                print("Coudn't get date")
            try:
                html = requests.get(website).text
                context = html_text.extract_text(html)
            except:
                print("Coudn't get website")
        Themen = row["Themen (aufteilen in Kurz Beschreibung und Schlagworten, danach löschen)"]
        if not pd.isna(Themen):
            Themen = Themen.replace("Alle", "").strip()
            if Themen:
                additionalContext += Themen + "\n"
        Fachbereich = row["Fachbereich / Material (aufteilen in Kurz Beschreibung und Schlagworten, danach löschen)"]
        if not pd.isna(Fachbereich):
            Fachbereich = Fachbereich.replace("Alle", "").strip()
            if Fachbereich:
                additionalContext += Fachbereich 
        totalContext = context
        if additionalContext:
            totalContext += "Schlagwörter hier in Schlagwörter und Kurzbeschreibung in Kurzbeschreibung integrieren: +\n" + additionalContext
        prompt = generatePrompt(Name)
        structuredPayload = generatePayload(models[0], prompt, totalContext)
        gotResult = False
        while not gotResult:
            try:
                result = generateTextFromText(structuredPayload)
                print(result)
                result = result["choices"][0]["message"]["content"]
                result = json.loads(result)
                gotResult = True
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
        print("\n")
        for column in optionalColumns:
            if pd.isna(row[column]):
                if result[column] != "":
                    df.at[index, column] = "<KI-Generiert> " + result[column]
        for column in facultativeColumns:
            if result[column] != "":
                df.at[index, column] = "<KI-Generiert> " + result[column]
        # delay of 5 seconds between requests
        time.sleep(5)
    # replace newlines in cells with spaces
    df = df.replace(r'\n', ' ', regex=True)
    # save df to csv 
    df.to_csv("output.csv", index=False)