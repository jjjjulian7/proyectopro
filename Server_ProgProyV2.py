import socket
import json
import threading
import sys
from clases.producto import Producto
from clases.inventario import Inventario
from datos import bd
import time

HOST = '192.168.1.119'
PORT = 65433
tiempo_maximo_carrito = 60
carritos_activos = {}
lock_carritos = threading.Lock()

def sweeper_thread():
    #eliminar carritos abandonados y restaurar stock
    while True:
        time.sleep(30) # revisa cada 30 segundos
        tiempo_actual = time.time()
        
        with lock_carritos:
            clientes_a_eliminar = []
            
            for ip_cliente, datos_carrito in carritos_activos.items():
                tiempo_ultima_accion = datos_carrito['tiempo']
                if (tiempo_actual - tiempo_ultima_accion) > tiempo_maximo_carrito:
                    print(f"[Sweeper] Carrito abandonado detectado para IP {ip_cliente}. Restaurando stock")
                    for item in datos_carrito['productos']:
                        bd.restaurar_stock(item['id_producto'], item['cantidad'])
                    clientes_a_eliminar.append(ip_cliente)
            
            
            for ip in clientes_a_eliminar: #elimina los carritos abandonados
                del carritos_activos[ip]
                
def iniciar_servidor():
    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    hilo_sweeper = threading.Thread(target=sweeper_thread, daemon=True) #hilo para eliminar carritos abandonados y restaurar stock
    hilo_sweeper.start()
    print("[+] Sweeper Thread (Garbage Collector) inicializado.")
    while True:
        socket_cliente, addr = server.accept()# se crea el socket donde se comunica con el cliente
        hilo_cliente=threading.Thread(target=atender_cliente,args=(socket_cliente,addr),daemon=True)
        hilo_cliente.start()


#manda mensaje a cliente segun el tipo de dato que recibio antes, esto se filtar a travez de procesar solicitud
def responder_cliente(socket_cliente,datos):
    mensaje=json.dumps(datos)+'\n'
    socket_cliente.sendall(mensaje.encode('utf-8'))

#filta por el tipo de mensaje que respondio
def procesar_solicitud(ip_cliente, socket_cliente,mensaje):
    tipo=mensaje.get('type')
    with lock_carritos: #with lock_carritos para asegurar que no haya conflictos al acceder a carritos_activos
        
        if ip_cliente not in carritos_activos:
            carritos_activos[ip_cliente] = {'tiempo': time.time(), 'productos': []} 
        else:
            carritos_activos[ip_cliente]['tiempo'] = time.time()
    if tipo=='reservar_stock':
        print(f"Servidor : Procesando solicitud de reservar stock {mensaje} \n" ) 
        id_producto=mensaje.get('id_producto')
        cantidad=mensaje.get('cantidad')
        nombre=mensaje.get('nombre')
        if not isinstance(cantidad,int) or cantidad <= 0:
            responder_cliente(socket_cliente,{'type': 'mensaje', 'mensaje': 'Cantidad inválida'})
            return
            
        acepto,respuesta, precio =bd.reservar_stock(id_producto,cantidad,nombre)
        if acepto:
            with lock_carritos: # se revisa si el cliente ya tiene un carrito activo y se actualiza el tiempo de la última acción
                carritos_activos[ip_cliente]['productos'].append({'id_producto': id_producto, 'cantidad': cantidad})
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
        with lock_carritos:
            for item in carritos_activos[ip_cliente]['productos']:
                if item['id_producto'] == id_producto:
                    item['cantidad'] -= cantidad
                    if item['cantidad'] <= 0:
                        carritos_activos[ip_cliente]['productos'].remove(item)
                    break
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
        with lock_carritos:
            carritos_activos[ip_cliente]['productos'].clear()
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
                procesar_solicitud(socket_cliente, mensaje, addr[0])
    except OSError:
        pass
    finally:
        socket_cliente.close()
        print(f"[-] Cliente desconectado: {addr}")
if __name__ == "__main__": iniciar_servidor()