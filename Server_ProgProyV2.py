import socket
import json
import threading
import sqlite3
from datos import bd
from datos import bd_carrito
from datos import bd_ventas
from datos import bd_envios
from clases.ListaDeseos import ListaDeseos, Suscripcion, Notificacion
from clases.asistente_ia import AsistenteIA

asistente_ia = AsistenteIA()
HOST = '192.168.1.112'
PORT = 65433


clientes_conectados = {}
lock_clientes = threading.Lock()   
lock_envio = threading.Lock()      
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
    with lock_envio:
        socket_cliente.sendall(mensaje.encode('utf-8'))

def _clp(valor):
    return f"${valor:,.0f}".replace(",", ".")

def _empujar_a_clientes(avisos):
    
    with lock_clientes:
        destinos=[(rut,clientes_conectados.get(rut),datos) for rut,datos in avisos]
    for rut,sock,datos in destinos:
        if sock is None:
            continue
        try:
            responder_cliente(sock,datos)
        except OSError:
            # socket roto: se saca del diccionario solo si sigue siendo el mismo
            with lock_clientes:
                if clientes_conectados.get(rut) is sock:
                    del clientes_conectados[rut]

def _avisar(ruts,id_producto,nombre,tipo,mensaje,extra=None):
    
    avisos=[]
    actual=datos_producto(id_producto) or {}
    for rut in ruts:
        Notificacion(rut,id_producto,mensaje).guardar()
        # precio, stock y categoria vigentes viajan en todo aviso para que el cliente pueda ofrecer "Agregar al carrito"
        datos={'type':'aviso','tipo':tipo,'id_producto':id_producto,'nombre':nombre,'mensaje':mensaje,
               'precio':actual.get('precio'),'stock':actual.get('stock'),'categoria':actual.get('categoria')}
        if extra:
            datos.update(extra)
        avisos.append((rut,datos))
    # el envio va en un hilo aparte: se llama desde el hilo de tkinter del admin y un cliente lento no debe congelarlo
    if avisos:
        threading.Thread(target=_empujar_a_clientes,args=(avisos,),daemon=True).start()
    return len(avisos)

def avisar_reposicion(id_producto):
    
    p=datos_producto(id_producto)
    if p is None:
        return 0
    mensaje=f"¡Volvió a haber stock de {p['nombre']}! Disponibles: {p['stock']}."
    return _avisar(Suscripcion.ruts_de_producto(id_producto),id_producto,p['nombre'],'reposicion',mensaje,
                   {'stock':p['stock'],'precio':p['precio']})

def avisar_rebaja(id_producto,precio_anterior,precio_nuevo):
    
    p=datos_producto(id_producto)
    if p is None:
        return 0
    mensaje=f"Rebaja en {p['nombre']}: antes {_clp(precio_anterior)}, ahora {_clp(precio_nuevo)}."
    return _avisar(ListaDeseos.ruts_con_deseo(id_producto),id_producto,p['nombre'],'rebaja',mensaje,
                   {'precio_anterior':precio_anterior,'precio_nuevo':precio_nuevo})

# el despacho es opcional para no romper ventas antiguas pero si viene se revisa completo
def despacho_valido(despacho):
    if despacho is None:
        return True
    if not isinstance(despacho,dict):
        return False
    modalidad=despacho.get('modalidad')
    costo=despacho.get('costo_envio')
    if not isinstance(costo,(int,float)) or costo<0:
        return False
    if modalidad==bd_ventas.MODALIDAD_RETIRO:
        return costo==0
    if modalidad!='Despacho a domicilio':
        return False
    for campo in ('destinatario','direccion','comuna','region'):
        valor=despacho.get(campo)
        if not isinstance(valor,str) or not valor.strip():
            return False
    try:
        tarifa = bd_envios.obtener_tarifa(despacho.get('region'))
        if tarifa is None:
            return False
        # revisa que el costo sea gratis por monto minimo o coincida con la tarifa actual
        return costo in (0, int(round(tarifa[1])))
    except sqlite3.Error:
        return False

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
    
    fila=bd.obtener_producto(id_producto)  # fila = (id, nombre, precio, stock, categoria)
    if fila is None:
        return None
    return {'id':fila[0],'nombre':fila[1],'precio':fila[2],'stock':fila[3],'categoria':fila[4]}

def armar_mi_lista(rut):
    
    deseos=[]
    for id_producto,precio_guardado in ListaDeseos(rut).items():
        p=datos_producto(id_producto)
        if p is not None:  # si el ADMIN elimino el producto, ya no se muestra
            p['precio_guardado']=precio_guardado
            deseos.append(p)
    suscripciones=[]
    for sus in Suscripcion.de_usuario(rut):
        p=datos_producto(sus.id_producto)
        if p is not None:
            suscripciones.append(p)
    notificaciones=[]
    for n in Notificacion.de_usuario(rut):
        p=datos_producto(n.id_producto)
        notificaciones.append({'id':n.id_producto,
                               'nombre':p['nombre'] if p else '(producto eliminado)',
                               'mensaje':n.mensaje})
    return deseos,suscripciones,notificaciones

#filta por el tipo de mensaje que respondio
def procesar_solicitud(socket_cliente,mensaje):
    tipo=mensaje.get('type')
    if tipo=='identificarse':
        rut=mensaje.get('rut')
        if not isinstance(rut,str) or not rut.strip():
            responder_cliente(socket_cliente,{'type':'identificarse','ok':False,'mensaje':'Datos inválidos'})
            return
        with lock_clientes:
            clientes_conectados[rut.strip()]=socket_cliente
        print(f"[+] Cliente identificado: {rut.strip()}")
        responder_cliente(socket_cliente,{'type':'identificarse','ok':True})
    elif tipo=='reservar_stock':
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
        if not venta_valida(mensaje) or not despacho_valido(mensaje.get('despacho')):
            responder_cliente(socket_cliente,{'type':'registrar_venta','ok':False,'mensaje':'Datos de la venta inválidos','recibo_id':None})
            return
        try:
            recibo_id=bd_ventas.insertar_venta(mensaje.get('fecha'),mensaje.get('cliente'),mensaje.get('total'),mensaje.get('items'),mensaje.get('despacho'))
            bd_carrito.marcar_pagado(mensaje.get('nombre_u'))
        except sqlite3.Error:
            responder_cliente(socket_cliente,{'type':'registrar_venta','ok':False,'mensaje':'No se pudo guardar la venta en el servidor','recibo_id':None})
            return
        responder_cliente(socket_cliente,{'type':'registrar_venta','ok':True,'mensaje':'Venta registrada correctamente','recibo_id':recibo_id})
    elif tipo=='obtener_envios':
        # manda al cliente las tarifas por region y el monto minimo desde el servidor
        try:
            tarifas = bd_envios.listar_tarifas()
            monto_minimo, region_tienda = bd_envios.obtener_config()
            lista_tarifas = [
                {'region': r, 'costo': c, 'dias_habiles': d}
                for r, c, d in tarifas
            ]
            responder_cliente(socket_cliente, {
                'type': 'obtener_envios',
                'ok': True,
                'tarifas': lista_tarifas,
                'monto_minimo': monto_minimo,
                'region_tienda': region_tienda
            })
        except sqlite3.Error:
            responder_cliente(socket_cliente, {
                'type': 'obtener_envios',
                'ok': False,
                'mensaje': 'No se pudieron consultar las tarifas de envío'
            })
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
        agregado=ListaDeseos(rut).agregar(id_producto,precio_actual)
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
        agregado=Suscripcion(rut,id_producto).guardar()
        mensaje_resp='Listo, te avisaremos cuando llegue.' if agregado else 'Ya estás suscrito a este producto.'
        responder_cliente(socket_cliente,{'type':'suscribir_reposicion','ok':True,'agregado':agregado,
                                          'mensaje':mensaje_resp,'id_producto':id_producto})
    elif tipo=='quitar_deseo':
        rut=mensaje.get('rut')
        id_producto=mensaje.get('id_producto')
        if not isinstance(rut,str) or not rut.strip() or not isinstance(id_producto,int):
            responder_cliente(socket_cliente,{'type':'mi_lista','ok':False,'mensaje':'Datos inválidos'})
            return
        ListaDeseos(rut).quitar(id_producto)
        deseos,suscripciones,notificaciones=armar_mi_lista(rut)   # se responde como mi_lista: el cliente refresca sus tablas
        responder_cliente(socket_cliente,{'type':'mi_lista','ok':True,'deseos':deseos,
                                          'suscripciones':suscripciones,'notificaciones':notificaciones})
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
        with lock_clientes:

            for rut in [r for r,sk in clientes_conectados.items() if sk is socket_cliente]:
                del clientes_conectados[rut]
        socket_cliente.close()
        print(f"[-] Cliente desconectado: {addr}")
if __name__ == "__main__": iniciar_servidor()