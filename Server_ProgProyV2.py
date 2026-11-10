import socket
import json
import threading
import sqlite3
from datos import bd
from datos import bd_carrito
from datos import bd_ventas
from datos import bd_deseos
from clases.asistente_ia import AsistenteIA

asistente_ia = AsistenteIA()
HOST = '10.190.94.2'
PORT = 65433
def iniciar_servidor():
    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
    except OSError:
        print(f"[-] El servidor ya está corriendo o el puerto {PORT} está en uso.")
        server.close()
        return
    server.listen()
    while True:
        socket_cliente, addr = server.accept()# se crea el socket donde se comunica con el cliente
        hilo_cliente=threading.Thread(target=atender_cliente,args=(socket_cliente,addr),daemon=True)
        hilo_cliente.start()


#manda mensaje a cliente segun el tipo de dato que recibio antes, esto se filtar a travez de procesar solicitud
def responder_cliente(socket_cliente,datos):
    mensaje=json.dumps(datos)+'\n'
    socket_cliente.sendall(mensaje.encode('utf-8'))

def venta_valida(mensaje):
    items=mensaje.get('items')
    if not isinstance(items,list) or not items:
        return False
    for item in items:
        if not isinstance(item,dict):
            return False
        if not isinstance(item.get('id'),int) or not isinstance(item.get('nombre'),str):
            return False
        if not isinstance(item.get('cantidad'),int) or item['cantidad']<=0:
            return False
        if not isinstance(item.get('precio'),(int,float)):
            return False
    return isinstance(mensaje.get('cliente'),str) and isinstance(mensaje.get('fecha'),str) and isinstance(mensaje.get('total'),(int,float))

def datos_producto(id_producto):
    """Nombre, precio, stock y categoria reales del producto, o None si fue eliminado."""
    fila=bd.obtener_producto(id_producto)  # fila = (id, nombre, precio, stock, categoria)
    if fila is None:
        return None
    return {'id':fila[0],'nombre':fila[1],'precio':fila[2],'stock':fila[3],'categoria':fila[4]}

def armar_mi_lista(rut):
    """Junta lo guardado en deseos.db con los datos actuales de los productos."""
    deseos=[]
    for id_producto,precio_guardado in bd_deseos.listar_deseos(rut):
        p=datos_producto(id_producto)
        if p is not None:  # si el ADMIN elimino el producto, ya no se muestra
            p['precio_guardado']=precio_guardado
            deseos.append(p)
    suscripciones=[]
    for (id_producto,) in bd_deseos.listar_suscripciones(rut):
        p=datos_producto(id_producto)
        if p is not None:
            suscripciones.append(p)
    notificaciones=[]
    for id_producto,texto in bd_deseos.listar_notificaciones(rut):
        p=datos_producto(id_producto)
        notificaciones.append({'id':id_producto,
                               'nombre':p['nombre'] if p else '(producto eliminado)',
                               'mensaje':texto})
    return deseos,suscripciones,notificaciones

#filta por el tipo de mensaje que respondio
def procesar_solicitud(socket_cliente,mensaje):
    tipo=mensaje.get('type')
    if tipo=='reservar_stock':
        print(f"Servidor : Procesando solicitud de reservar stock {mensaje} \n" ) 
        id_producto=mensaje.get('id_producto')
        cantidad=mensaje.get('cantidad')
        nombre=mensaje.get('nombre')
        nombre_u = mensaje.get('nombre_u')
        if not isinstance(cantidad,int) or cantidad <= 0:
            responder_cliente(socket_cliente,{'type': 'mensaje', 'mensaje': 'Cantidad inválida'})
            return
            
        acepto,respuesta, precio =bd.reservar_stock(id_producto,cantidad,nombre)
        if acepto:
            bd_carrito.agregar_item(nombre_u, id_producto, nombre, cantidad, precio)
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
        nombre_u=mensaje.get('nombre_u')
        en_carrito=0
        if isinstance(id_producto,int) and isinstance(cantidad,int) and cantidad >= 0:
            en_carrito=bd_carrito.cantidad_en_carrito(nombre_u, id_producto)
        if en_carrito==0:
            responder_cliente(socket_cliente,{'type':'reponer_stock',
                                              'ok':False,
                                              'id_producto':id_producto,
                                              'mensaje':'El producto no está en el carrito',
                                              'cantidad':0})
            return
        cantidad=min(cantidad,en_carrito)
        bd.restaurar_stock(id_producto,cantidad)
        bd_carrito.quitar_item(nombre_u, id_producto, cantidad)
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
        bd_carrito.vaciar_carrito_usuario(mensaje.get('nombre_u'))
        responder_cliente(socket_cliente,{'type':'vaciar_carrito', 'ok':exito, 'mensaje':'Carrito vaciado correctamente'})
    elif tipo=='registrar_venta':
        if not venta_valida(mensaje):
            responder_cliente(socket_cliente,{'type':'registrar_venta','ok':False,'mensaje':'Datos de la venta inválidos','recibo_id':None})
            return
        try:
            recibo_id=bd_ventas.insertar_venta(mensaje.get('fecha'),mensaje.get('cliente'),mensaje.get('total'),mensaje.get('items'))
            bd_carrito.marcar_pagado(mensaje.get('nombre_u'))
        except sqlite3.Error:
            responder_cliente(socket_cliente,{'type':'registrar_venta','ok':False,'mensaje':'No se pudo guardar la venta en el servidor','recibo_id':None})
            return
        responder_cliente(socket_cliente,{'type':'registrar_venta','ok':True,'mensaje':'Venta registrada correctamente','recibo_id':recibo_id})
    elif tipo=='agregar_deseo':
        # el servidor valida con los datos reales: el cliente solo dice QUIEN (rut) y QUE producto
        rut=mensaje.get('rut')
        id_producto=mensaje.get('id_producto')
        if not isinstance(rut,str) or not rut.strip() or not isinstance(id_producto,int):
            responder_cliente(socket_cliente,{'type':'agregar_deseo','ok':False,'mensaje':'Datos inválidos'})
            return
        producto=bd.obtener_producto(id_producto)
        if producto is None:
            responder_cliente(socket_cliente,{'type':'agregar_deseo','ok':False,'mensaje':'El producto ya no existe'})
            return
        precio_actual=producto[2]  # fila = (id, nombre, precio, stock, categoria)
        agregado=bd_deseos.agregar_deseo(id_producto,rut,precio_actual)
        mensaje_resp='Producto agregado a tu lista de deseos.' if agregado else 'Este producto ya está en tu lista de deseos.'
        responder_cliente(socket_cliente,{'type':'agregar_deseo','ok':True,'agregado':agregado,
                                          'mensaje':mensaje_resp,'id_producto':id_producto})
    elif tipo=='suscribir_reposicion':
        rut=mensaje.get('rut')
        id_producto=mensaje.get('id_producto')
        if not isinstance(rut,str) or not rut.strip() or not isinstance(id_producto,int):
            responder_cliente(socket_cliente,{'type':'suscribir_reposicion','ok':False,'mensaje':'Datos inválidos'})
            return
        producto=bd.obtener_producto(id_producto)
        if producto is None:
            responder_cliente(socket_cliente,{'type':'suscribir_reposicion','ok':False,'mensaje':'El producto ya no existe'})
            return
        if producto[3]>0:  # fila[3] = stock real en este instante
            responder_cliente(socket_cliente,{'type':'suscribir_reposicion','ok':False,
                                              'mensaje':'Este producto tiene stock disponible, el aviso es solo para productos agotados.'})
            return
        agregado=bd_deseos.agregar_suscripcion(id_producto,rut)
        mensaje_resp='Listo, te avisaremos cuando llegue.' if agregado else 'Ya estás suscrito a este producto.'
        responder_cliente(socket_cliente,{'type':'suscribir_reposicion','ok':True,'agregado':agregado,
                                          'mensaje':mensaje_resp,'id_producto':id_producto})
    elif tipo=='mi_lista':
        rut=mensaje.get('rut')
        if not isinstance(rut,str) or not rut.strip():
            responder_cliente(socket_cliente,{'type':'mi_lista','ok':False,'mensaje':'Datos inválidos'})
            return
        deseos,suscripciones,notificaciones=armar_mi_lista(rut)
        responder_cliente(socket_cliente,{'type':'mi_lista','ok':True,'deseos':deseos,
                                          'suscripciones':suscripciones,'notificaciones':notificaciones})
    elif tipo=='consulta_ia':
        pregunta = mensaje.get('pregunta', '')
        print(f"Servidor : Consulta para asistente IA: {pregunta}")
        def responder_ia():
            ok, texto_respuesta = asistente_ia.consultar(pregunta)
            responder_cliente(socket_cliente, {
                'type': 'consulta_ia',
                'ok': ok,
                'respuesta': texto_respuesta
            })
        hilo_ia = threading.Thread(target=responder_ia, daemon=True)
        hilo_ia.start()

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