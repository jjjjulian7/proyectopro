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
        notificacion TEXT ,
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS suscripciones(
        rut TEXT NOT NULL,
        id_producto INTEGER NOT NULL)
        '''
    )
    conexion.commit()
    conexion.close()

def mostrar_lista(rut):
    conexion=conectar()
    cursor=conexion.cursor()

    cursor.execute(
        '''
        SELECT u.rut,u.nombre_usuario,l.nombre,l.precio,l.stock,l.categoria
        from deseos u  
        INNER JOIN lista l ON l.rut=u.rut
        where u.rut=?
        ''',(rut,)
    )

def crear_lista_o_buscar(rut,nombre_usuarios):
    conexion=conectar()
    cursor=conexion.cursor()
    cursor.execute(
        '''
        SELECT rut,nombre_usuario
        FROM deseos
        WHERE rut=? AND nombre_usuarios=?
        ''',(rut,nombre_usuarios)
    )
    fila=cursor.fetchone()
    if fila is None:
        return fila[0]
    
    cursor.execute(
        '''
        INSERT INTO deseos(rut,nombre_usuarios) VALUES (?,?)
        ''',(rut,nombre_usuarios)
    )
    conexion.commit()
    conexion.close()
    
    return cursor.lastrowid()




def agregar_producto(id_producto,rut,nombre_usuario,nombre,precio,stock,categoria):
    conexion=conectar()
    cursor=conexion.cursor()
    r=crear_lista_o_buscar(rut,nombre_usuario)
    cursor.execute(
        '''
        INSERT INTO lista (id_producto,rut,nombre,precio,stock,goria) VALUES (?,r,?,?,?,?)
        ''',(id_producto,nombre,precio,stock,categoria)
    )


def notificacion(id_producto,categoria_notificacion,):
    conexion=conectar()
    cursor=conexion.cursor()
    
    cursor.execute(#me devolvera los rut en donde el producto actualizado se encuentre en su lista
        '''
        SELECT rut 
        FROM lista 
        WHERE id_producto=?
        ''',(id_producto,)
    )
    filas=cursor.fetchall()
    
    for (rut,) in filas:#recorrera cada lista de los usuarios
        if categoria_notificacion=='p':#si se actualizo el precio
            cursor.execute(
            '''
            UPDATE lista
            SET notificacion=?
            WHERE rut=? AND id_producto=?
            '''
        ,("se rebajo el precio del producto",rut,id_producto,))
            conexion.commit()
        if categoria_notificacion=='s':
            cursor.execute(
                        '''
                        UPDATE lista
                        SET notificacion=?
                        WHERE rut=? AND id_producto=?
                        '''
                    ,("se actualizo el stock del producto",rut,id_producto,))
            conexion.commit
        conexion.close()
