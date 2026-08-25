import sqlite3
from clases import usuario
import os
ruta_bd=os.path.join(
    os.path.dirname(os.path.dirname(__file__)),"usuarios.db")
def conectar():
    conexion = sqlite3.connect(ruta_bd) # Se conecta a la bd si no existe se crea sola
    return conexion

def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contrasena TEXT NOT NULL
        )
    ''')

    conexion.commit()
    conexion.close()
def insertar_usuario(usuario):

    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO usuarios (nombre, contrasena)
        VALUES (?, ?)
    ''', (usuario.nombre, usuario.contrasena))
    usuario.id = cursor.lastrowid
    conexion.commit()
    conexion.close()

def buscar_usuario(nombre):
    conexion=conectar()
    cursor=conexion.cursor()
    cursor.execute(''' SELECT *
    FROM usuarios
    WHERE nombre=?
    ''',(nombre,))
    resultado=cursor.fetchone()

    conexion.close
    return resultado
