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
    conexion.commit()
    conexion.close()


def insertar_venta(fecha, cliente, total):
    crear_tabla()  # por si la tabla todavia no existe
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO ventas (fecha, cliente, total) VALUES (?, ?, ?)",
        (fecha, cliente, total)
    )
    id_venta = cursor.lastrowid  # id automatico, sera el numero del recibo
    conexion.commit()
    conexion.close()
    return id_venta