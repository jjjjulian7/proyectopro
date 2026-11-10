import sqlite3
import os
from datetime import datetime


ruta_bd=os.path.join(
    os.path.dirname(os.path.dirname(__file__)),"deseos.db") #busca una ruta especifica para la base de datos de usuarios no importa donde se ejecute el programa, la base de datos se crea en la carpeta raiz del proyecto
def conectar():
    conexion = sqlite3.connect(ruta_bd) # se conecta a la bd si no existe se crea sola
    return conexion
def crear_tabla():
    conexion=conectar()
    cursor=conexion.cursor()
    #tabla del producto que esta relacionada al usuario
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS lista(
        id_producto INTEGER ,
        rut TEXT NOT NULL,
        precio_actualizado REAL NOT NULL,
        notificacion TEXT,

        UNIQUE(rut,id_producto)
        )
    '''
    )
    #tabla de notificaciones
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS notificaciones(
        rut TEXT NOT NULL,
        id_producto INTEGER,
        notificacion TEXT)
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS suscripciones(
        rut TEXT NOT NULL,
        id_producto INTEGER NOT NULL,
        UNIQUE(rut,id_producto))
        '''
    )
    conexion.commit()
    conexion.close()

def notificacion(id_producto,categoria_notificacion):
    """Deja anotado en la lista de cada usuario que el producto cambio (p = precio, s = stock)."""
    crear_tabla()
    conexion=conectar()
    try:
        cursor=conexion.cursor()
        texto={'p':"se rebajo el precio del producto",'s':"se actualizo el stock del producto"}.get(categoria_notificacion)
        if texto is None:
            return
        cursor.execute(
            '''
            UPDATE lista
            SET notificacion=?
            WHERE id_producto=?
            ''',(texto,id_producto)
        )
        conexion.commit()
    finally:
        conexion.close() #se cierra una sola vez y aunque falle la consulta


def agregar_deseo(id_producto,rut,precio):
    crear_tabla()
    conexion=conectar()
    cursor=conexion.cursor()
    cursor.execute(
        '''
        INSERT OR IGNORE INTO lista(id_producto,rut,precio_actualizado) VALUES (?,?,?)
        ''',(id_producto,rut,precio)
    )
    agregado=cursor.rowcount>0 #si ya estaba en la lista el UNIQUE lo ignora y rowcount queda en 0
    conexion.commit()
    conexion.close()
    return agregado

def agregar_suscripcion(id_producto,rut):
    crear_tabla()
    conexion=conectar()
    cursor=conexion.cursor()
    cursor.execute(
        '''
        SELECT 1 FROM suscripciones WHERE rut=? AND id_producto=?
        ''',(rut,id_producto)
    )
    if cursor.fetchone() is not None:
        conexion.close()
        return False
    cursor.execute(
        '''
        INSERT INTO suscripciones(rut,id_producto) VALUES (?,?)
        ''',(rut,id_producto)
    )
    conexion.commit()
    conexion.close()
    return True


def _consultar(sql,params):
    crear_tabla()  #si el usuario abre la ventana antes de agregar algo, las tablas aun no existen
    conexion=conectar()
    try:
        cursor=conexion.cursor()
        cursor.execute(sql,params)
        return cursor.fetchall()
    finally:
        conexion.close()

def listar_deseos(rut):
    """[(id_producto, precio guardado)] en el orden en que se agregaron."""
    return _consultar("SELECT id_producto,precio_actualizado FROM lista WHERE rut=? ORDER BY rowid",(rut,))

def listar_suscripciones(rut):
    """[(id_producto,)] de los productos a los que el usuario pidio aviso de reposicion."""
    return _consultar("SELECT id_producto FROM suscripciones WHERE rut=? ORDER BY rowid",(rut,))

def listar_notificaciones(rut):
    """[(id_producto, mensaje)] la mas reciente primero."""
    return _consultar("SELECT id_producto,notificacion FROM notificaciones WHERE rut=? ORDER BY rowid DESC",(rut,))

def guardar_notificacion(rut,id_producto,mensaje):
    crear_tabla()
    conexion=conectar()
    try:
        conexion.execute("INSERT INTO notificaciones(rut,id_producto,notificacion) VALUES (?,?,?)",(rut,id_producto,mensaje))
        conexion.commit()
    finally:
        conexion.close()