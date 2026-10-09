import socket
import json
import threading
import sys
from clases.producto import Producto
from clases.inventario import Inventario
from datos import bd

HOST = '192.168.1.119'
PORT = 65433
def iniciar_servidor():
    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    while True:
        socket_cliente, addr = server.accept()# se crea el socket donde se comunica con el cliente
        hilo_cliente=threading.Thread(target=atender_cliente,args=(socket_cliente,addr),daemon=True)
        hilo_cliente.start()


#manda mensaje a cliente segun el tipo de dato que recibio antes, esto se filtar a travez de procesar solicitud
def responder_cliente(socket_cliente,datos):
    mensaje=json.dumps(datos)+'\n'
    socket_cliente.sendall(mensaje.encode('utf-8'))

#filta por el tipo de mensaje que respondio
def procesar_solicitud(socket_cliente,mensaje):
    tipo=mensaje.get('type')
    if tipo=='reservar_stock':
        print(f"Servidor : Procesando solicitud de reservar stock {mensaje} \n" ) 
        id_producto=mensaje.get('id_producto')
        cantidad=mensaje.get('cantidad')
        nombre=mensaje.get('nombre')
        if not isinstance(cantidad,int) or cantidad <= 0:
            responder_cliente(socket_cliente,{'type': 'mensaje', 'mensaje': 'Cantidad inválida'})
            return
            
        acepto,respuesta, precio =bd.reservar_stock(id_producto,cantidad,nombre)
        responder_cliente(socket_cliente,{'type':'reservar_stock',
                                              'ok':acepto,
                                              'mensaje':respuesta,
                                              'id_producto':id_producto,
                                              'cantidad':cantidad,
                                              'nombre':nombre,
                                              'precio':precio})
    elif tipo=='reponer_stock':
        id_producto=mensaje.get('id_producto')
        cantidad=mensaje.get('cantidad')
        bd.restaurar_stock(id_producto,cantidad)
        responder_cliente(socket_cliente,{'type':'reponer_stock',
                                          'ok':True,
                                          'id_producto':id_producto,
                                            'mensaje':'Stock repuesto correctamente',
                                            'cantidad':cantidad})
    elif tipo=='vaciar_carrito':
        lista_productos=mensaje.get('productos', [])
        print(f"Servidor: Procesando solicitud de vaciar carrito: {mensaje}")
        exito=True
        for item in lista_productos:
            id_producto=item.get('id_producto')
            cantidad=item.get('cantidad')
            bd.restaurar_stock(id_producto,cantidad)
        responder_cliente(socket_cliente,{'type':'vaciar_carrito', 'ok':exito, 'mensaje':'Carrito vaciado correctamente'})

def atender_cliente(socket_cliente, addr):
    print(f"[+] Cliente conectado: {addr}")
    buffer = b""
    try:
        while True:
            data = socket_cliente.recv(4096)
            if not data:
                break

            buffer += data
            while b'\n' in buffer:
                linea, buffer = buffer.split(b'\n', 1)
                if not linea.strip():
                    continue
                try:
                    mensaje = json.loads(linea.decode('utf-8'))
                except json.JSONDecodeError:
                    print("[!] Mensaje con JSON inválido")
                    continue
                procesar_solicitud(socket_cliente, mensaje)
    except OSError:
        pass
    finally:
        socket_cliente.close()
        print(f"[-] Cliente desconectado: {addr}")
if __name__ == "__main__": iniciar_servidor()