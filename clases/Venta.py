import json
import os
from datetime import datetime
import datos.bd_ventas as bd_ventas


class venta:
    def __init__(self, cliente, items, total):
        self.recibo_id = None  # lo asigna la base de datos al guardar
        self.fecha = datetime.now().isoformat(timespec="seconds")
        self.cliente = cliente
        self.items = items  # lista de productos del carrito
        self.total = total

    def guardar_en_bd(self):
        # Guarda la venta en la bd y recibe el id automatico
        self.recibo_id = bd_ventas.insertar_venta(self.fecha, self.cliente, self.total)

    def guardar_json(self):
        carpeta = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recibos")
        os.makedirs(carpeta, exist_ok=True)  # crea la carpeta si no existe
        ruta = os.path.join(carpeta, f"recibo_{self.recibo_id}.json")
        with open(ruta, "w", encoding="utf-8") as f:
            # default=lambda o: o.__dict__ convierte el objeto venta a JSON usando sus atributos
            json.dump(self, f, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
        return ruta