import socket
import json
import threading
import sys
import time
from tkinter import messagebox
HOST = '172.20.10.3'
PORT = 65433

conexion=None
c=False
# conexiones hacia el servidor, se hace en un hilo para que no se congele la interfaz
conexion_reserva=None
conexion_reponer=None
conexion_vaciar=None

def conectar_interfaz_reserva(conexion):
    global conexion_reserva
    conexion_reserva = conexion

def conectar_interfaz_reponer(conexion):
    global conexion_reponer
    conexion_reponer = conexion

def conectar_interfaz_vaciar(conexion):
    global conexion_vaciar
    conexion_vaciar = conexion
    
def conectar():
    """utiliza las variables globales conexion y c para conectarse con el admin """
    global conexion , c #se ocupa variables globales porque despues se ocupara el socket conexion para mandar la info
    while not c:
        intento=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            intento.settimeout(5)
            intento.connect((HOST,PORT))
            intento.settimeout(None)
            print ("se conecto correctamente")
            conexion=intento
            c=True
            hilo_recibir=threading.Thread(target=recibir,args=(intento,),daemon=True)
            hilo_recibir.start()
        except OSError:
            intento.close()
            time.sleep(3)
            print("no se pudo conectar con el administrador")

def enviar(dato):
    if conexion is None:
        messagebox.showwarning("no se puede mandar al server", "no conexion con servidor")
        return False
    mensaje_transformado=json.dumps(dato)
    mensaje_transformado+='\n'
    conexion.sendall(mensaje_transformado.encode('utf-8'))
    return True

def recibir(socket_conexion):
    bufer=''
    while True:
        mensaje=socket_conexion.recv(4096)
        if not mensaje:
            break
        bufer+=mensaje.decode('utf-8')
        while '\n' in bufer:
            mensaje_completo,bufer=bufer.split('\n',1)
            if not mensaje_completo.strip():
                continue
            try:
                dato=json.loads(mensaje_completo)
            except json.JSONDecodeError:
                continue
            tipo=dato.get('type')
            if tipo=='reservar_stock':
                ok=dato.get('ok')
                mensaje=dato.get('mensaje')
                id_producto=dato.get('id_producto')
                cantidad=dato.get('cantidad')
                nombre=dato.get('nombre')
                precio=dato.get('precio')
                if conexion_reserva is not None:
                    conexion_reserva(ok,mensaje,id_producto,cantidad,nombre,precio)
            elif tipo=='reponer_stock':
                ok=dato.get('ok')
                if conexion_reponer is not None:
                    conexion_reponer(ok)
            elif tipo=='vaciar_carrito':
                ok=dato.get('ok')
                mensaje=dato.get('mensaje')
                if conexion_vaciar is not None:
                    conexion_vaciar(ok, mensaje)
                

def dato_envia(dato):
    tipo=dato.get('type')
    if tipo == 'reservar_stock':
        id_producto=dato.get('id_producto')
        cantidad=dato.get('cantidad')
        nombre=dato.get('nombre')
        enviar({'type':'reservar_stock',
            'id_producto':id_producto,
                    'cantidad':cantidad,
                    'nombre':nombre})
    elif tipo =='reponer_stock':
        id_producto=dato.get('id_producto')
        cantidad=dato.get('cantidad')
        enviar({'type':'reponer_stock',
            'id_producto':id_producto,
                'cantidad':cantidad})
    elif tipo == 'vaciar_carrito':
        productos=dato.get('productos', [])
        enviar({'type':'vaciar_carrito', 'productos':productos})