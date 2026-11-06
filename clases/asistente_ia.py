import http.client
import json
from datos import bd

# configuración
API_KEY = ""  

try:
    archivo = open("api_key.txt", "r")
    API_KEY = archivo.read().strip()
    archivo.close()
except:
    pass

MODELO = "gemini-2.5-flash"
HOST = "generativelanguage.googleapis.com"
PATH = f"/v1/models/{MODELO}:generateContent?key={API_KEY}"


class AsistenteIA:
    def __init__(self):
        self.modelo = MODELO
        self.host = HOST
        self.path = PATH
        self.headers = {
            "Content-Type": "application/json"
        }

    def obtener_catalogo(self):
        productos = bd.mostrar_productos()
        texto_productos = "Productos disponibles en la tienda:\n"
        for p in productos:
            # p[0]=id, p[1]=nombre, p[2]=precio, p[3]=stock, p[4]=categoria
            texto_productos += f"- {p[1]} (Categoria: {p[4]}) Precio: ${p[2]} Stock: {p[3]}\n"
        return texto_productos

    def consultar(self, pregunta):
        catalogo = self.obtener_catalogo()

        body = {
            "contents": [
                {
                    "parts": [
                        {"text": f"Eres el asistente de nuestra tienda online. {catalogo}\nPregunta del cliente: {pregunta}"}
                    ]
                }
            ]
        }

        
        body_json = json.dumps(body)

        # conexion con gemini
        conn = http.client.HTTPSConnection(self.host)
        conn.request("POST", self.path, body=body_json, headers=self.headers)

        # almacenar respuesta 
        response = conn.getresponse()
        data = response.read().decode("utf-8")
        conn.close()

        # verificar de respuesta 
        if response.status == 200:
            response_data = json.loads(data)
            respuesta_texto = response_data["candidates"][0]["content"]["parts"][0]["text"]
            print("Respuesta de Gemini:")
            print(respuesta_texto)
            return True, respuesta_texto
        else:
            print(f"Error: {response.status} - {response.reason}")
            print(data)
            return False, f"Error: {response.status} - {response.reason}"
