import sqlite3
import os

ruta_bd = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ventas.db")  # ventas.db en la raiz del proyecto


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
    conexion.commit()
    conexion.close()


def insertar_venta(fecha, cliente, total, items):
    crear_tabla()  # por si la tabla todavia no existe
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO ventas (fecha, cliente, total) VALUES (?, ?, ?)",
        (fecha, cliente, total)
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