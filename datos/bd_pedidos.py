import sqlite3
import os
from datetime import datetime
from clases.pedido import EstadoPedido

ruta_bd = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pedidos.db")


def conectar():
    return sqlite3.connect(ruta_bd)


def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            numero INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            cliente TEXT,
            estado TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedido_historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER NOT NULL,
            estado TEXT NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (numero) REFERENCES pedidos(numero)
        )
    ''')
    conexion.commit()
    conexion.close()


def _ahora():
    return datetime.now().isoformat(timespec="seconds")


def crear_pedido(venta_id, cliente):
    """Crea el pedido en estado Pendiente y devuelve su número."""
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    fecha = _ahora()
    cursor.execute(
        "INSERT INTO pedidos (venta_id, cliente, estado, fecha) VALUES (?, ?, ?, ?)",
        (venta_id, cliente, EstadoPedido.PENDIENTE, fecha)
    )
    numero = cursor.lastrowid
    cursor.execute(
        "INSERT INTO pedido_historial (numero, estado, fecha) VALUES (?, ?, ?)",
        (numero, EstadoPedido.PENDIENTE, fecha)
    )
    conexion.commit()
    conexion.close()
    return numero


def obtener_pedido(numero):
    """Devuelve (numero, venta_id, cliente, estado, fecha) o None."""
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT numero, venta_id, cliente, estado, fecha FROM pedidos WHERE numero = ?",
        (numero,)
    )
    fila = cursor.fetchone()
    conexion.close()
    return fila


def cambiar_estado(numero, nuevo_estado):
    """Valida la transición con EstadoPedido y la guarda. Devuelve (ok, mensaje)."""
    fila = obtener_pedido(numero)
    if fila is None:
        return False, "El pedido no existe."
    actual = fila[3]
    if nuevo_estado not in EstadoPedido.TRANSICIONES.get(actual, []):
        return False, f"No se puede pasar de {actual} a {nuevo_estado}."
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE pedidos SET estado = ? WHERE numero = ?", (nuevo_estado, numero))
    cursor.execute(
        "INSERT INTO pedido_historial (numero, estado, fecha) VALUES (?, ?, ?)",
        (numero, nuevo_estado, _ahora())
    )
    conexion.commit()
    conexion.close()
    return True, f"Pedido N°{numero}: {nuevo_estado}"


def listar_por_estado():
    """Para el panel del ADMIN: {estado: [(numero, venta_id, cliente, fecha), ...]}."""
    crear_tabla()
    grupos = {estado: [] for estado in EstadoPedido.TRANSICIONES}
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT numero, venta_id, cliente, estado, fecha FROM pedidos ORDER BY numero")
    for numero, venta_id, cliente, estado, fecha in cursor.fetchall():
        grupos[estado].append((numero, venta_id, cliente, fecha))
    conexion.close()
    return grupos