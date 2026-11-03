import urllib.request
import json

API_KEY = ""  # Agrega tu API key de Gemini aquí
url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"

req = urllib.request.Request(url, method="GET")
try:
    with urllib.request.urlopen(req) as response:
        modelos = json.loads(response.read().decode("utf-8"))
        print("--- Modelos disponibles en tu proyecto ---")
        for modelo in modelos.get("models", []):
            print(f"- {modelo['name']}")
except urllib.error.HTTPError as e:
    print(f"Error: {e.code}")
    print(e.read().decode("utf-8"))