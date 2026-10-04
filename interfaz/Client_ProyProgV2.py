import socket
import json
import threading
import sys
import time
from tkinter import messagebox
HOST = '192.168.1.119'
PORT = 65433

conexion=None
c=False
def conectar():
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
    mensaje_transformado=json.dumps(dato)+'\n'
    mensaje_transformado=mensaje_transformado.encode('utf-8')
    conexion.sendall(mensaje_transformado)
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
    if tipo =='reponer_stock':
        id_producto=dato.get('id_producto')
        cantidad=dato.get('cantidad')
        enviar({'type':'reponer_stock',
            'id_producto':id_producto,
                'cantidad':cantidad})