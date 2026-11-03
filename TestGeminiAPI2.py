import http.client
import json

# Configuración
API_KEY = ""  # Agrega tu API key de Gemini aquí

MODELO = "gemini-3.5-flash"
HOST = "generativelanguage.googleapis.com"
PATH = f"/v1/models/{MODELO}:generateContent?key={API_KEY}"

#Estrucutra de peticiones estandar para Gemini
headers = {
    "Content-Type": "application/json"
}

body = {
    "contents": [
        {
            "parts": [
                {"text":"como te puedo conectar a mi proyecto de una tienda online con sockets y tkinder en python? usando hilos?"}
            ]
        }
    ]
}

# Enviar peticion aplicando estructura JSON Estandar para Gemini
body_json = json.dumps(body)

#Conexion a Gemini Mediante HTTP Client y POST
conn = http.client.HTTPSConnection(HOST)
conn.request("POST", PATH, body=body_json, headers=headers)

#Almacenar respuesta de Gemini usando UFT 8
response = conn.getresponse()
data = response.read().decode("utf-8")
conn.close()

#Verificar de respuesta exitosa desde Gemini
if response.status == 200:
    response_data = json.loads(data)
    print("Respuesta de Gemini:")
    print(response_data["candidates"][0]["content"]["parts"][0]["text"])
else:
    print(f"Error: {response.status} - {response.reason}")
    print(data)
