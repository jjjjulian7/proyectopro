import sqlite3
import os

ruta_bd = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ventas.db")  # ventas.db en la raiz del proyecto

MODALIDAD_RETIRO = "Retiro en tienda"

# columnas de entrega de cada venta (se agregan solas si la bd es antigua)
COLUMNAS_DESPACHO = [
    ("modalidad", "TEXT NOT NULL DEFAULT 'Retiro en tienda'"),
    ("destinatario", "TEXT"),
    ("direccion", "TEXT"),
    ("comuna", "TEXT"),
    ("region", "TEXT"),
    ("costo_envio", "REAL NOT NULL DEFAULT 0"),
    ("fecha_entrega", "TEXT"),
]


def conectar():
    return sqlite3.connect(ruta_bd)  # Se conecta a la bd, si no existe se crea sola


def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            cliente TEXT,
            total REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venta_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id)
        )
    ''')

    # si ventas.db ya existia sin las columnas de despacho se las agregamos sin perder las ventas
    columnas = [fila[1] for fila in cursor.execute("PRAGMA table_info(ventas)").fetchall()]
    for nombre, definicion in COLUMNAS_DESPACHO:
        if nombre not in columnas:
            cursor.execute(f"ALTER TABLE ventas ADD COLUMN {nombre} {definicion}")

    conexion.commit()
    conexion.close()


def insertar_venta(fecha, cliente, total, items, despacho=None):
    crear_tabla()  # por si la tabla todavia no existe
    despacho = despacho or {}  # las ventas sin despacho se guardan como retiro en tienda
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO ventas (fecha, cliente, total, modalidad, destinatario, direccion, comuna, region, "
        "costo_envio, fecha_entrega) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (fecha, cliente, total,
         despacho.get("modalidad") or MODALIDAD_RETIRO,
         despacho.get("destinatario"), despacho.get("direccion"),
         despacho.get("comuna"), despacho.get("region"),
         despacho.get("costo_envio") or 0, despacho.get("fecha_entrega"))
    )
    id_venta = cursor.lastrowid  # id automatico, sera el numero del recibo
    for item in items:
        cursor.execute(
            "INSERT INTO venta_items (venta_id, id_producto, nombre, cantidad, precio) VALUES (?, ?, ?, ?, ?)",
            (id_venta, item["id"], item["nombre"], item["cantidad"], item["precio"])
        )
    conexion.commit()
    conexion.close()
    return id_venta


def listar_ventas():
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, fecha, cliente, total FROM ventas ORDER BY id DESC")
    ventas = cursor.fetchall()
    conexion.close()
    return ventas


def items_de_venta(venta_id):
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id_producto, nombre, cantidad, precio, cantidad * precio FROM venta_items WHERE venta_id = ?",
        (venta_id,)
    )
    items = cursor.fetchall()
    conexion.close()
    return items


# datos de entrega de una venta como diccionario o None si la venta no existe
def obtener_despacho(venta_id):
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    fila = cursor.execute(
        "SELECT modalidad, destinatario, direccion, comuna, region, costo_envio, fecha_entrega "
        "FROM ventas WHERE id = ?", (venta_id,)
    ).fetchone()
    conexion.close()
    if fila is None:
        return None
    claves = ("modalidad", "destinatario", "direccion", "comuna", "region", "costo_envio", "fecha_entrega")
    return dict(zip(claves, fila))


# diccionario {id_venta: modalidad} para la columna entrega de la lista de ventas del admin
def modalidades_por_venta():
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    filas = cursor.execute("SELECT id, modalidad FROM ventas").fetchall()
    conexion.close()
    return dict(filas)
