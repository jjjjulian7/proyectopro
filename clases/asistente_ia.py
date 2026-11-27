import http.client
import json
import os
import ssl
import sys
import time

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

MODELO = "gemini-3.8-flash"
MODELOS_DISPONIBLES = ("gemini-3.8-flash", "gemini-3.6-flash")
HOST = "generativelanguage.googleapis.com"
PATH = f"/v1beta/models/{MODELO}:generateContent?key={API_KEY}"


class AsistenteIA:
    def __init__(self):
        self.modelo = MODELO
        self.host = HOST
        self.path = PATH
        self.historial = []
        self.headers = {
            "Content-Type": "application/json"
        }

    def obtener_catalogo(self, ids_carrito=None):
        if ids_carrito is None:
            ids_carrito = set()
        productos = bd.productos_disponibles()
        texto_productos = "Productos disponibles en la tienda:\n"
        for p in productos:
            # p[0]=id, p[1]=nombre, p[2]=precio, p[3]=stock, p[4]=categoria
            if p[0] not in ids_carrito:
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
            return "Carrito actual del cliente: Vacio.\n", set()

        items = bd_carrito.items_de_carrito(carrito_id)
        if not items:
            return "Carrito actual del cliente: Vacio.\n", set()

        ids_carrito = set()
        texto_carrito = "Productos en el carrito del cliente:\n"
        for i in items:
            # i[0]=id_producto, i[1]=nombre, i[2]=cantidad, i[3]=precio, i[4]=subtotal
            ids_carrito.add(i[0])
            texto_carrito += f"- {i[1]} Cantidad: {i[2]} Precio: ${i[3]} Subtotal: ${i[4]}\n"
        return texto_carrito, ids_carrito

    def obtener_historial(self):
        if not self.historial:
            return ""
        texto_historial = "Mensajes anteriores:\n"
        for m in self.historial[-5:]:
            texto_historial += f"Cliente: {m['pregunta']}\nAsistente: {m['respuesta']}\n"
        return texto_historial

    def obtener_recomendados(self, respuesta_texto, ids_carrito=None):
        if ids_carrito is None:
            ids_carrito = set()
        productos = bd.productos_disponibles()
        recomendados = []
        ids_agregados = set()
        texto_minuscula = respuesta_texto.lower()
        for p in productos:
            # p[0]=id, p[1]=nombre, p[2]=precio, p[3]=stock, p[4]=categoria
            if p[0] not in ids_carrito and p[0] not in ids_agregados and p[1].lower() in texto_minuscula:
                ids_agregados.add(p[0])
                recomendados.append({
                    "id": p[0],
                    "nombre": p[1],
                    "precio": p[2],
                    "stock": p[3]
                })
        return recomendados

    def respaldo_destacados(self, ids_carrito=None):
        if ids_carrito is None:
            ids_carrito = set()
        productos = bd.productos_destacados()
        recomendados = []
        mensaje = "Lo siento, no podemos atender tu pregunta en este momento por alta demanda. Inténtalo más tarde.\n"
        for p in productos:
            if p[0] not in ids_carrito:
                recomendados.append({
                    "id": p[0],
                    "nombre": p[1],
                    "precio": p[2],
                    "stock": p[3]
                })
                if len(recomendados) == 3:
                    break

        if recomendados:
            mensaje += "Si te interesa, estos son nuestros productos más destacados disponibles:\n"
            for prod in recomendados:
                mensaje += f"- {prod['nombre']} (${prod['precio']:,.0f} CLP - Stock: {prod['stock']})\n"
        return mensaje, recomendados

    def consultar(self, pregunta, nombre_usuario=None):
        carrito, ids_carrito = self.obtener_carrito(nombre_usuario)

        if not API_KEY:
            return False, "Error: Falta agregar la API key en api_key.txt", []

        catalogo = self.obtener_catalogo(ids_carrito)
        historial = self.obtener_historial()

        if not self.historial:
            regla_saludo = "Al inicio de esta respuesta, saluda y preséntate brevemente como el asistente de Maulencitos Market."
        else:
            regla_saludo = "Ya te presentaste en mensajes anteriores, así que no vuelvas a saludar ni presentarte; ve directo al punto."

        prompt = (
            f"Eres el asistente virtual de la tienda online Maulencitos Market (tienda de tecnología y computación). {regla_saludo} "
            "Responde ÚNICAMENTE sobre productos, precios, stock y compras de esta tienda usando solo el catálogo y carrito entregados, sin inventar productos ni precios. "
            "Si el cliente hace una pregunta fuera de tema o sobre cosas que no vendemos (por ejemplo comida como un kilo de pollo, chistes, tareas o productos inexistentes), indícale amablemente que solo puedes ayudarlo con los productos tecnológicos de Maulencitos Market y sugiérele alternativas disponibles del catálogo. "
            "Responde de forma clara y específica para resolver la pregunta del cliente. "
            "Cuando recomiendes un producto, escribe su nombre exacto tal como aparece en el catálogo. "
            "Revisa el carrito del cliente: si está vacío, concéntrate solo en responder su pregunta. "
            "Si el carrito tiene productos y se relacionan con la pregunta, conecta tu recomendación con lo que ya lleva (por ejemplo: 'Veo que ya tienes X, te recomiendo complementarlo con Y'); "
            "si no tienen relación directa, agrega al final una recomendación breve de un producto del catálogo que complemente su carrito. "
            "Termina siempre con una pregunta abierta corta sobre la tienda para que el cliente pueda seguir la conversación.\n\n"
            f"{catalogo}\n{carrito}\n{historial}\nPregunta del cliente: {pregunta}"
        )

        body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        body_json = json.dumps(body)

        try:
            import certifi
            contexto = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            contexto = ssl.create_default_context()

        for intento, modelo_actual in enumerate(MODELOS_DISPONIBLES):
            path = f"/v1beta/models/{modelo_actual}:generateContent?key={API_KEY}"
            try:
                conn = http.client.HTTPSConnection(self.host, timeout=20, context=contexto)
                conn.request("POST", path, body=body_json, headers=self.headers)
                response = conn.getresponse()
                data = response.read().decode("utf-8")
                conn.close()
            except Exception as e:
                print(f"Error de conexion ({modelo_actual}):", e)
                if intento == 0:
                    time.sleep(1)
                continue

            if response.status == 200:
                response_data = json.loads(data)
                partes = response_data["candidates"][0]["content"]["parts"]
                respuesta_texto = "".join(parte.get("text", "") for parte in partes if not parte.get("thought"))
                if respuesta_texto.strip():
                    self.historial.append({"pregunta": pregunta, "respuesta": respuesta_texto})
                    recomendados = self.obtener_recomendados(respuesta_texto, ids_carrito)
                    print("Respuesta de Gemini:")
                    print(respuesta_texto)
                    return True, respuesta_texto, recomendados
            else:
                print(f"Error ({modelo_actual}): {response.status} - {response.reason}")
                print(data)
                if response.status in (400, 403):
                    break
                if intento == 0:
                    time.sleep(1)

        mensaje_respaldo, recomendados = self.respaldo_destacados(ids_carrito)
        return False, mensaje_respaldo, recomendados

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
