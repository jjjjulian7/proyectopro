import sqlite3
from clases.usuario import usuario
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
            nombre TEXT,
            rut TEXT,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'usuario'
        )
    ''')

    # Si la BD ya existía antes del cambio, revisamos si faltan columnas nuevas
    columnas = cursor.execute('PRAGMA table_info(usuarios)').fetchall()
    nombres_columnas = [columna[1] for columna in columnas]

    if 'rut' not in nombres_columnas:
        cursor.execute('ALTER TABLE usuarios ADD COLUMN rut TEXT')
    if 'rol' not in nombres_columnas:
        cursor.execute('ALTER TABLE usuarios ADD COLUMN rol TEXT NOT NULL DEFAULT "usuario"')

    conexion.commit()
    conexion.close()

def insertar_usuario(usuario):
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO usuarios (nombre, rut, contrasena, rol)
        VALUES (?, ?, ?, ?)
    ''', (usuario.nombre, usuario.rut, usuario.contrasena, usuario.rol))
    usuario.id = cursor.lastrowid
    conexion.commit()
    conexion.close()

# Funciones hechas por Sebastian Leon 
def buscar_usuario(nombre):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE nombre = ?', (nombre,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado


def buscar_usuario_por_rut(rut):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE rut = ?', (rut,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado

def convertir_en_admin(nombre, rut):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE usuarios SET rut = ?, rol = 'admin' WHERE nombre = ?",
        (rut, nombre)
    )
    conexion.commit()
    conexion.close()


def crear_admin_por_defecto():
    if buscar_usuario_por_rut('12.345.678-9') is None:      
        insertar_usuario(usuario('admin', 'admin123', 'admin', '12.345.678-9'))

# Busca al usuario según la pantalla desde la que intenta entrar.
# Si viene del login de admin, busca por rut. si viene del login normal, busca por nombre
def buscar_usuario_por_tipo(tipo, valor):
    conexion = conectar()
    cursor = conexion.cursor()

    if tipo == 'admin':
        cursor.execute(
            "SELECT * FROM usuarios WHERE rut = ? AND rol = 'admin'",
            (valor,),
        )
    else:
        cursor.execute(
            "SELECT * FROM usuarios WHERE nombre = ? AND rol = 'usuario'",
            (valor,),
        )

    resultado = cursor.fetchone()
    conexion.close()
    return resultado
