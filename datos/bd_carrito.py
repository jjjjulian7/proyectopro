import sqlite3
import os
from datetime import datetime

ruta_bd=os.path.join(
    os.path.dirname(os.path.dirname(__file__)),"carrito.db") #busca una ruta especifica para la base de datos de usuarios no importa donde se ejecute el programa, la base de datos se crea en la carpeta raiz del proyecto
def conectar():
    conexion = sqlite3.connect(ruta_bd) # se conecta a la bd si no existe se crea sola
    return conexion

#se crean 2 tablas, una donde esta informacion del carrito como el usuario y cuando se creo, la otra contiene los productos del carrito en donde esta tiene una clave foreana que la conecta con el carrito
def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carritos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'activo'
        )
    ''')
    # Cada fila es un producto dentro de un carrito
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carrito_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carrito_id INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            FOREIGN KEY (carrito_id) REFERENCES carritos(id)
        )
    ''')
    conexion.commit()
    conexion.close()


def obtener_o_crear_carrito(nombre_usuario):
    """Devuelve el id del carrito activo del usuario. Si no tiene, se crea uno nuevo."""
    crear_tabla()
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id FROM carritos WHERE nombre_usuario = ? AND estado = 'activo'",
            (nombre_usuario,)
        )
        fila = cursor.fetchone()
        if fila is not None:
            return fila[0]

        fecha = datetime.now().isoformat(timespec="seconds")
        cursor.execute(
            "INSERT INTO carritos (nombre_usuario, fecha_creacion, estado) VALUES (?, ?, 'activo')",
            (nombre_usuario, fecha)
        )
        conexion.commit()
        return cursor.lastrowid
    finally:
        conexion.close()


def agregar_item(nombre_usuario, id_producto, nombre, cantidad, precio):
    """se llama cuando el servidor acepta (reserva stock) un producto.
    si el producto ya estaba en el carrito suma la cantidad, si no crea la fila."""
    carrito_id = obtener_o_crear_carrito(nombre_usuario)
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id FROM carrito_items WHERE carrito_id = ? AND id_producto = ?",
            (carrito_id, id_producto)
        )
        fila = cursor.fetchone()
        if fila is None:
            cursor.execute(
                "INSERT INTO carrito_items (carrito_id, id_producto, nombre, cantidad, precio) VALUES (?, ?, ?, ?, ?)",
                (carrito_id, id_producto, nombre, cantidad, precio)
            )
        else:
            cursor.execute(
                "UPDATE carrito_items SET cantidad = cantidad + ?, precio = ? WHERE id = ?",
                (cantidad, precio, fila[0])
            )
        conexion.commit()
        return carrito_id
    finally:
        conexion.close()


def quitar_item(nombre_usuario, id_producto, cantidad):
    """Resta cantidad de un producto del carrito activo; si llega a 0 borra la fila."""
    crear_tabla()
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id FROM carritos WHERE nombre_usuario = ? AND estado = 'activo'",
            (nombre_usuario,)
        )
        carrito = cursor.fetchone()
        if carrito is None:
            return
        cursor.execute(
            "UPDATE carrito_items SET cantidad = cantidad - ? WHERE carrito_id = ? AND id_producto = ?",
            (cantidad, carrito[0], id_producto)
        )
        cursor.execute("DELETE FROM carrito_items WHERE carrito_id = ? AND cantidad <= 0", (carrito[0],))
        conexion.commit()
    finally:
        conexion.close()


def vaciar_carrito_usuario(nombre_usuario):
    """Borra todos los items del carrito activo del usuario."""
    crear_tabla()
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id FROM carritos WHERE nombre_usuario = ? AND estado = 'activo'",
            (nombre_usuario,)
        )
        carrito = cursor.fetchone()
        if carrito is None:
            return
        cursor.execute("DELETE FROM carrito_items WHERE carrito_id = ?", (carrito[0],))
        conexion.commit()
    finally:
        conexion.close()


def marcar_pagado(nombre_usuario):
    """Cierra el carrito activo despues de pagar (el proximo producto creara uno nuevo)."""
    crear_tabla()
    conexion = conectar()
    try:
        conexion.execute(
            "UPDATE carritos SET estado = 'pagado' WHERE nombre_usuario = ? AND estado = 'activo'",
            (nombre_usuario,)
        )
        conexion.commit()
    finally:
        conexion.close()


def listar_carritos():
    """Para la ventana admin: (id, usuario, fecha, estado, total_items, total_$) por carrito."""
    crear_tabla()
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute('''
            SELECT c.id, c.nombre_usuario, c.fecha_creacion, c.estado,
                   COALESCE(SUM(i.cantidad), 0),
                   COALESCE(SUM(i.cantidad * i.precio), 0)
            FROM carritos c
            LEFT JOIN carrito_items i ON i.carrito_id = c.id
            GROUP BY c.id
            ORDER BY c.id DESC
        ''')
        return cursor.fetchall()
    finally:
        conexion.close()


def items_de_carrito(carrito_id):
    """Para la ventana admin: (id_producto, nombre, cantidad, precio, subtotal) del carrito."""
    crear_tabla()
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id_producto, nombre, cantidad, precio, cantidad * precio FROM carrito_items WHERE carrito_id = ?",
            (carrito_id,)
        )
        return cursor.fetchall()
    finally:
        conexion.close()