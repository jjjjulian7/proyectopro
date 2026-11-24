import http.client
import json
import ssl
from datos import bd

# configuración
API_KEY = ""  

try:
    archivo = open("api_key.txt", "r")
    API_KEY = archivo.read().strip()
    archivo.close()
except:
    pass

if not API_KEY:
    print("AVISO: no se encontro api_key.txt (o esta vacio), se busca en la carpeta desde donde se ejecuta el servidor")

MODELO = "gemini-3.8-flash"
HOST = "generativelanguage.googleapis.com"
PATH = f"/v1beta/models/{MODELO}:generateContent?key={API_KEY}"


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

        # si esta instalado certifi se usan sus certificados (el python de msys2 no trae los suyos)
        try:
            import certifi
            contexto = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            contexto = ssl.create_default_context()

        # conexion con gemini, si algo falla se devuelve el error para que le llegue al chat y no se quede esperando
        try:
            conn = http.client.HTTPSConnection(self.host, timeout=30, context=contexto)
            conn.request("POST", self.path, body=body_json, headers=self.headers)

            # almacenar respuesta 
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()
        except ssl.SSLCertVerificationError:
            print("Error: python no tiene certificados para conectarse a Google (instalar certifi o ca-certificates)")
            return False, "Error: Python no tiene certificados SSL instalados para conectarse a Google."
        except (OSError, http.client.HTTPException) as e:
            print(f"Error de conexion con gemini: {e}")
            return False, f"Error de conexión con Gemini: {e}"

        # verificar de respuesta 
        if response.status == 200:
            response_data = json.loads(data)
            # los modelos nuevos pueden devolver varias partes, se juntan todas las de texto
            partes = response_data["candidates"][0]["content"]["parts"]
            respuesta_texto = "".join(parte.get("text", "") for parte in partes if not parte.get("thought"))
            print("Respuesta de Gemini:")
            print(respuesta_texto)
            return True, respuesta_texto
        else:
            print(f"Error: {response.status} - {response.reason}")
            print(data)
            # google manda el motivo del error dentro del json, se lo pasamos al chat para saber que paso
            motivo = ""
            try:
                motivo = json.loads(data)["error"]["message"]
            except (ValueError, KeyError, TypeError):
                pass
            return False, f"Error: {response.status} - {response.reason}\n{motivo}"
