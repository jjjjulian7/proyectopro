import sqlite3
from clases.usuario import usuario
import os
ruta_bd=os.path.join(
    os.path.dirname(os.path.dirname(__file__)),"usuarios.db") #busca una ruta especifica para la base de datos de usuarios no importa donde se ejecute el programa, la base de datos se crea en la carpeta raiz del proyecto
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
    columnas = cursor.execute('PRAGMA table_info(usuarios)').fetchall() #PRAGMA pide la informacion de la tabla parecido a SELECT * FROM  pero devuelve una lista de tuplas con la informacion de la tabla
    nombres_columnas = [columna[1] for columna in columnas] # Extrae los nombres de las columnas de la lista de tuplas

    if 'rut' not in nombres_columnas:
        cursor.execute('ALTER TABLE usuarios ADD COLUMN rut TEXT') #busca la columna rut y si no existe la agrega
    if 'rol' not in nombres_columnas:
        cursor.execute('ALTER TABLE usuarios ADD COLUMN rol TEXT NOT NULL DEFAULT "usuario"') #busca la columna rol y si no existe la agrega

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
    usuario.id = cursor.lastrowid #lastrowid devuelve el id del ultimo registro insertado en la tabla
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
        "UPDATE usuarios SET rut = ?, rol = 'admin' WHERE nombre = ?", #Set cambia el rol del usuario a admin y actualiza su rut
        (rut, nombre)
    )
    conexion.commit()
    conexion.close()


def crear_admin_por_defecto(): #crea un usuario admin por defecto si no existe en la base de datos
    if buscar_usuario_por_rut('12.345.678-9') is None:      # revisa si el usuario admin por defecto ya existe en la base de datos, si no existe lo crea
        insertar_usuario(usuario('admin', 'admin123', 'admin', '12.345.678-9'))

# Busca al usuario según la pantalla desde la que intenta entrar.
# Si viene del login de admin, busca por rut. si viene del login normal, busca por nombre
def buscar_usuario_por_tipo(tipo, valor):
    conexion = conectar()
    cursor = conexion.cursor()

    if tipo == 'admin':
        cursor.execute(
            "SELECT * FROM usuarios WHERE rut = ? AND rol = 'admin'",
            (valor,), #devuelve una tupla con el valor del rut para evitar errores de sintaxis en la consulta SQL
        )
    else:
        cursor.execute(
            "SELECT * FROM usuarios WHERE nombre = ? AND rol = 'usuario'",
            (valor,),
        )

    resultado = cursor.fetchone()
    conexion.close()
    return resultado
