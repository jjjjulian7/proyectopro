import http.client
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datos import bd
from datos import bd_carrito

# configuración
API_KEY = ""

try:
    ruta_key = os.path.join(os.path.dirname(os.path.dirname(__file__)), "api_key.txt")
    archivo = open(ruta_key, "r")
    API_KEY = archivo.read().strip()
    archivo.close()
except:
    pass

MODELO = "gemini-4-hydrogen"
HOST = "generativelanguage.googleapis.com"
PATH = f"/v1/models/{MODELO}:generateContent?key={API_KEY}"


class AsistenteIA:
    def __init__(self):
        self.modelo = MODELO
        self.host = HOST
        self.path = PATH
        self.historial = []
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

    def obtener_carrito(self, nombre_usuario=None):
        carritos = bd_carrito.listar_carritos()
        # c[0] = id, #c[1] = nombre_usuario, #c[2] = fecha_creacion #c[3] = estado
        carrito_id = None
        for c in carritos:
            if c[3] == "activo":
                if nombre_usuario is None or c[1] == nombre_usuario:
                    carrito_id = c[0]
                    break

        if carrito_id is None:
            return "Carrito actual del cliente: Vacio.\n"

        items = bd_carrito.items_de_carrito(carrito_id)
        if not items:
            return "Carrito actual del cliente: Vacio.\n"

        texto_carrito = "Productos en el carrito del cliente:\n"
        for i in items:
            texto_carrito += f"- {i[1]} Cantidad: {i[2]} Precio: ${i[3]} Subtotal: ${i[4]}\n"
        return texto_carrito

    def obtener_historial(self):
        if not self.historial:
            return ""
        texto_historial = "Mensajes anteriores:\n"
        for m in self.historial[-5:]:
            texto_historial += f"Cliente: {m['pregunta']}\nAsistente: {m['respuesta']}\n"
        return texto_historial

    def obtener_recomendados(self, respuesta_texto):
        productos = bd.mostrar_productos()
        recomendados = []
        texto_minuscula = respuesta_texto.lower()
        for p in productos:
            # p[0]=id, p[1]=nombre, p[2]=precio, p[3]=stock, p[4]=categoria
            if p[3] > 0 and p[1].lower() in texto_minuscula:
                recomendados.append({
                    "id": p[0],
                    "nombre": p[1],
                    "precio": p[2],
                    "stock": p[3]
                })
        return recomendados

    def consultar(self, pregunta, nombre_usuario=None):
        if not API_KEY:
            return False, "Error: Falta agregar la API key en api_key.txt", []

        catalogo = self.obtener_catalogo()
        carrito = self.obtener_carrito(nombre_usuario)
        historial = self.obtener_historial()

        body = {
            "contents": [
                {
                    "parts": [
                        {"text": f"Eres el asistente de nuestra tienda online, presentate ante el usuario primero antes de responder su pregunta, menciona que eres parte de la tienda Maulencitos Market, quiero respuestas especificas que solucionen la pregunta del cliente, y al final una pregunta abierta donde el cliente puede seguir la conversacion, cuando recomiendes un producto escribe su nombre exacto tal como aparece en el catalogo, no olvides revisar el carrito del cliente para ver que es lo que ya tiene lanzarle una pequeña recomendacion pero solo corta como veo que tienes esto si te interesa te reccomiendo tal cosa, solo hacer eso cuando el carrito no este vacio, si esta vacio solo concentrate en la pregunta, si lo q tiene en el carrito tiene q ver con lo que pregunta el cliente, hablale sobre tu recomendacion mas loq  tiene el carrito por ejemplo veo q tienes esto y ahi sigues. {catalogo}\n{carrito}\n{historial}\nPregunta del cliente: {pregunta}"}
                    ]
                }
            ]
        }

        body_json = json.dumps(body)

        try:
            # conexion con gemini
            conn = http.client.HTTPSConnection(self.host, timeout=3000)
            conn.request("POST", self.path, body=body_json, headers=self.headers)

            # almacenar respuesta
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()
        except Exception as e:
            print("Error de conexion:", e)
            return False, "Error: No se pudo conectar con el servidor de Gemini", []

        # verificar de respuesta
        if response.status == 200:
            response_data = json.loads(data)
            respuesta_texto = response_data["candidates"][0]["content"]["parts"][0]["text"]
            self.historial.append({"pregunta": pregunta, "respuesta": respuesta_texto})
            recomendados = self.obtener_recomendados(respuesta_texto)
            print("Respuesta de Gemini:")
            print(respuesta_texto)
            return True, respuesta_texto, recomendados
        else:
            print(f"Error: {response.status} - {response.reason}")
            print(data)
            return False, f"Error: {response.status} - {response.reason}", []

    def limpiar_historial(self):
        self.historial.clear()

# codigo temporal para correr la ia en la consola y hacer las pruebas
if __name__ == "__main__":
    asistente = AsistenteIA()
    while True:
        pregunta = input("\nCliente: ")
        if pregunta.lower() == "salir":
            asistente.limpiar_historial()
            break
        ok, respuesta, recomendados = asistente.consultar(pregunta)
        print(f"\nAsistente:\n{respuesta}")
        if recomendados:
            print("\nProductos detectados para agregar al carrito:", recomendados)
