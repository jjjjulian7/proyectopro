import json
import os
from datetime import datetime
import datos.bd_ventas as bd_ventas


class venta:
    def __init__(self, cliente, items, subtotal, iva, total, despacho=None, costo_envio=0):
        self.recibo_id = None  # lo asigna la base de datos al guardar
        self.fecha = datetime.now().isoformat(timespec="seconds")
        self.cliente = cliente
        self.items = [dict(item) for item in items]  # diccionario de productos del carrito
        self.subtotal = subtotal
        self.iva = iva
        self.total = total
        self.despacho = despacho or {}   # dict de entrega 
        self.costo_envio = costo_envio

    def guardar_en_bd(self):
        # Guarda la venta en la bd y recibe el id automatico
        self.recibo_id = bd_ventas.insertar_venta(self.fecha, self.cliente, self.total, self.items, self.despacho)

    def a_diccionario(self):    # Armamos el diccionario con el formato de como saldra el JSON
        return {
            "recibo_id": self.recibo_id,
            "fecha": self.fecha,
            "cliente": self.cliente,
            "items": [
                {
                    "id": item["id"],
                    "nombre": item["nombre"],
                    "cantidad": item["cantidad"],
                    "precio": item["precio"],
                    "subtotal": item["precio"] * item["cantidad"],
                }
                for item in self.items
            ],
            "subtotal": round(self.subtotal, 2),
            "envio": round(self.costo_envio, 2),
            "iva": round(self.iva, 2),
            "total": round(self.total, 2),
            "despacho": {
                "modalidad": self.despacho.get("modalidad", "Retiro en tienda"),
                "destinatario": self.despacho.get("destinatario"),
                "direccion": self.despacho.get("direccion"),
                "comuna": self.despacho.get("comuna"),
                "region": self.despacho.get("region"),
                "costo_envio": round(self.costo_envio, 2),
                "fecha_entrega_estimada": self.despacho.get("fecha_entrega"),
            },
        }

    def guardar_json(self):
        carpeta = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recibos")
        os.makedirs(carpeta, exist_ok=True)  # crea la carpeta si no existe
        ruta = os.path.join(carpeta, f"recibo_{self.recibo_id}.json")
        with open(ruta, "w", encoding="utf-8") as f:
            # default=lambda o: o.__dict__ convierte el objeto venta a JSON usando sus atributos
            json.dump(self.a_diccionario(), f, indent=4, ensure_ascii=False)
        return ruta