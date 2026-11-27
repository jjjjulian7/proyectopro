import threading
from types import SimpleNamespace
from interfaz import Client_ProyProgV2 as ClienteRed
from tkinter import messagebox
from clases.Venta import venta 
from datos import bd_cupones
from clases.envio import Despacho, TarifaEnvio
from clases.direccion import Direccion

class Carrito:
    def __init__(self):
        self.items = []
        self.cupon = 0.0
        self.tipo_cupon = "porcentaje"
        self.codigo_cupon = None
        self.despacho = Despacho()  # por defecto retiro en tienda sin costo de envio
        self.usuario=None
        self.expirado = False
        self.funcion_dibujar_tabla = None  # Inicializamos la función como None
        self.evento_venta = threading.Event()
        self.respuesta_venta = None
        # tarifas y configuracion que llegan desde el servidor
        self.tarifas_envio = {}
        self.monto_minimo_envio = 100000
        self.region_tienda = "Maule"
        self.evento_envios = threading.Event()
        self.envios_cargados = False
    
    def agregar_producto(self, producto, cantidad,usuario):
        print(f"Usuario : Agregando producto {producto.nombre}, Cantidad: {cantidad}" )
        self.usuario=usuario
        self.expirado = False
        ClienteRed.dato_envia({'type' : 'reservar_stock',
                               'id_producto' : producto.id,
                               'cantidad' : cantidad,
                               'nombre': producto.nombre,
                                'nombre_u':usuario}) #llama a la funcion reservar_stock de bd.py para reservar el stock del producto

    def agregar_recomendado(self, id_producto, recomendados, usuario=None):
        if self.expirado:
            self.items.clear()
            self.cupon = 0.0
            self.codigo_cupon = None
            self.despacho = Despacho()
            self.expirado = False

        encontrado = None
        for prod in recomendados:
            if prod["id"] == id_producto:
                encontrado = prod
                break

        if encontrado is None or encontrado.get("stock", 0) <= 0:
            return False

        for item in self.items:
            if str(item["id"]) == str(id_producto):
                recomendados.remove(encontrado)
                return False

        usuario_final = usuario if usuario is not None else self.usuario
        producto_obj = SimpleNamespace(id=encontrado["id"], nombre=encontrado["nombre"])
        self.agregar_producto(producto_obj, 1, usuario_final)
        recomendados.remove(encontrado)
        return True
        
    def procesar_respuesta_reservar(self, ok, mensaje, id_producto, cantidad, nombre, precio):
        if ok:
            for item in self.items: #recorre los items del carrito y si el producto ya existe, aumenta la cantidad
                if item["id"] == id_producto: #compara el id del producto con los items del carrito
                    item["cantidad"] += cantidad
                    if self.funcion_dibujar_tabla is not None:
                        self.funcion_dibujar_tabla()  # Llama a la función para actualizar la interfaz
                    return 
            self.items.append({ #agrega un nuevo producto al carrito si no existe
                "id": id_producto, # se agrega id para identificar el producto mas facil 
                "cantidad": cantidad,
                "precio" :precio,
                "nombre": nombre
            })
            if self.funcion_dibujar_tabla is not None:
                self.funcion_dibujar_tabla()  # Llama a la función para actualizar la interfaz
        else:
            messagebox.showwarning("Error al agregar producto", mensaje)
        
    # funciones matematicas para calcular el subtotal el envio el iva y el total del carrito
    def calcular_subtotal(self):
        subtotal = 0
        for item in self.items:
            subtotal += item["precio"] * item["cantidad"]
        if self.tipo_cupon == "monto_fijo":
            subtotal = max(0, subtotal - self.cupon)
        else:
            subtotal = subtotal * (1 - self.cupon)
        return subtotal

    # si es retiro o el subtotal llega al monto minimo el envio sale gratis
    def calcular_envio(self):
        return self.despacho.calcular_costo(self.calcular_subtotal())
    
    # el iva ahora se calcula sobre el subtotal mas el envio
    def calcular_iva(self):
        base = self.calcular_subtotal() + self.calcular_envio()
        return base * 0.19  # 19% de IVA
    
    # al total se le suma el envio
    def calcular_total(self):
        return self.calcular_subtotal() + self.calcular_envio() + self.calcular_iva()

    # pide las tarifas actualizadas al servidor por socket
    def pedir_tarifas_servidor(self, esperar=True):
        if ClienteRed.conexion is None:
            return False
        self.evento_envios.clear()
        try:
            ClienteRed.dato_envia({'type': 'obtener_envios'})
        except OSError:
            return False
        if esperar:
            return self.evento_envios.wait(2)
        return True

    # guarda las tarifas que respondio el servidor
    def procesar_respuesta_envios(self, dato):
        if dato.get('ok'):
            nuevas = {}
            for item in dato.get('tarifas', []):
                region = item.get('region')
                if region:
                    nuevas[region] = TarifaEnvio(region, item.get('costo', 0), item.get('dias_habiles', 0))
            self.tarifas_envio = nuevas
            self.monto_minimo_envio = dato.get('monto_minimo', 100000)
            self.region_tienda = dato.get('region_tienda', "Maule")
            self.envios_cargados = True
            if not self.despacho.es_retiro() and self.despacho.direccion is not None:
                self.despacho.tarifa = self.tarifas_envio.get(self.despacho.direccion.region)
                self.despacho.monto_minimo = self.monto_minimo_envio
        self.evento_envios.set()

    def regiones_disponibles(self):
        return list(self.tarifas_envio.keys())

    # manejo del despacho
    # el cliente retira en tienda asi que no paga envio
    def elegir_retiro(self):
        self.despacho = Despacho()

    # revisa los datos y la region contra las tarifas recibidas del servidor
    # si algo falla deja el despacho como estaba y devuelve el motivo
    def elegir_despacho(self, destinatario, calle, comuna, region):
        if not self.envios_cargados:
            self.pedir_tarifas_servidor(esperar=True)
        if not self.tarifas_envio:
            return False, "No se pudo consultar las tarifas de envío en el servidor."
        direccion = Direccion(destinatario, calle, comuna, region)
        ok, motivo = direccion.validar(self.regiones_disponibles())
        if not ok:
            return False, motivo
        tarifa = self._leer_tarifa(direccion.region)
        monto_minimo = self.monto_minimo_envio
        self.despacho = Despacho(Despacho.DOMICILIO, direccion, tarifa, monto_minimo)
        return True, ""

    # con solo la region ya se puede mostrar el envio y la fecha estimada
    # los demas campos se revisan recien al pagar
    def previsualizar_despacho(self, region):
        if not self.envios_cargados:
            self.pedir_tarifas_servidor(esperar=True)
        tarifa = self._leer_tarifa(region)
        if tarifa is None:
            return False
        anterior = self.despacho.direccion
        direccion = Direccion(anterior.destinatario if anterior else "", anterior.calle if anterior else "",
                              anterior.comuna if anterior else "", region)
        self.despacho = Despacho(Despacho.DOMICILIO, direccion, tarifa, self.monto_minimo_envio)
        return True

    def _leer_tarifa(self, region):
        return self.tarifas_envio.get(region)

    # se llama justo antes de cobrar por si el admin cambio las tarifas mientras el cliente compraba
    def _revalidar_despacho(self):
        if self.despacho.es_retiro():
            return True, ""
        d = self.despacho.direccion
        if d is None:
            return False, "Completa los datos de despacho."
        if not self.pedir_tarifas_servidor(esperar=True) or not self.tarifas_envio:
            return False, "No se pudo consultar las tarifas de envío en el servidor."
        ok, motivo = d.validar(self.regiones_disponibles())
        if not ok:
            return False, motivo
        self.despacho.tarifa = self._leer_tarifa(d.region)
        self.despacho.monto_minimo = self.monto_minimo_envio
        return True, ""
    
    def vaciar_carrito(self):
        print("Usuario : Enviando solicitud al servidor para vaciar carrito")
        productos_a_devolver = []
        for item in self.items: #recorre los items del carrito y restaura el stock de cada producto en la base de datos
            productos_a_devolver.append({
                "id_producto": item["id"],
                "cantidad": item["cantidad"]})
        print(f"Productos a devolver stock: {productos_a_devolver}")
        ClienteRed.dato_envia({'type' : 'vaciar_carrito', 'productos' : productos_a_devolver,'nombre_u': self.usuario})
            
    def procesar_respuesta_vaciar(self, ok, mensaje):
        if ok:
            self.items.clear()  # Vacía el carrito después de procesar la compra
            self.cupon = 0.0
            self.codigo_cupon = None
            print("Carrito vaciado correctamente \n")
            messagebox.showinfo("Carrito vaciado", "El carrito ha sido vaciado correctamente.")
            if self.funcion_dibujar_tabla is not None:
                self.funcion_dibujar_tabla()  # Llama a la función para actualizar la interfaz
        else:
            messagebox.showwarning("Error al vaciar carrito", mensaje)
        
    def eliminar_producto(self, id_producto, cantidad):
        print("Soliciando eliminar producto)\n")
        ClienteRed.dato_envia({'type': 'reponer_stock', 'id_producto' : id_producto, 'cantidad' : cantidad,'nombre_u' : self.usuario })
        
    def procesar_respuesta_eliminar(self, ok, id_producto, cantidad, mensaje):
        print("rastreo de eliminar producto")
        print(f"ok: {ok}, mensaje: {mensaje}, cantidad: {cantidad}, id_producto: {id_producto}")
        if ok:
            if cantidad <=0:
                return 
            print("carrito actual antes de eliminar producto: ", self.items)

            for item in self.items:
                print(f"Comparando item id: {item['id']} con id_producto: {id_producto}")
                if str(item["id"]) == str(id_producto):
                    print(f"Producto encontrado en carrito: {item}")
                    if cantidad >= item["cantidad"]:
                        cantidad = item["cantidad"]  # Ajusta la cantidad a eliminar si es mayor que la cantidad en el carrito
                    item["cantidad"] -= cantidad  # se resta la cantidad eliminada del producto en el carrito
                    if item["cantidad"] <= 0:
                        self.items.remove(item)
                        print("Producto eliminado del carrito: ", item)
                    if self.funcion_dibujar_tabla is not None:
                        self.funcion_dibujar_tabla()
                        print("tabla actualizada despues de eliminar producto")
                    break
        else:
            print("Error al eliminar producto: ", mensaje)
            messagebox.showwarning("Error al eliminar producto", mensaje)

    def procesar_respuesta_venta(self, ok, mensaje, recibo_id):
        self.respuesta_venta = (ok, mensaje, recibo_id)
        self.evento_venta.set()

    def procesar_compra(self, cliente):
        if not self.items:
            return False, "El carrito está vacío", None

        # revisa que el despacho este bien antes de cobrar
        try:
            despacho_ok, motivo = self._revalidar_despacho()
        except Exception as e:
            despacho_ok, motivo = False, f"No se pudo consultar las tarifas de envío: {e}"
        if not despacho_ok:
            if self.funcion_dibujar_tabla is not None:
                self.funcion_dibujar_tabla()
            return False, motivo, None
        costo_envio = self.calcular_envio()
        datos_despacho = self.despacho.a_diccionario(costo_envio)

        # la venta ahora guarda tambien el despacho y el costo de envio
        nueva_venta = venta(cliente, self.items, self.calcular_subtotal(), self.calcular_iva(), self.calcular_total(),
                            datos_despacho, costo_envio)
        self.respuesta_venta = None
        self.evento_venta.clear()
        if ClienteRed.conexion is None:
            return False, "No hay conexión con el servidor", None
        try:
            # se manda tambien el despacho al servidor
            ClienteRed.dato_envia({'type': 'registrar_venta', 'cliente': cliente, 'fecha': nueva_venta.fecha, 'items': nueva_venta.items, 'total': nueva_venta.total, 'despacho': datos_despacho, 'nombre_u': self.usuario})
        except OSError:
            return False, "No se pudo enviar la venta al servidor", None
        if not self.evento_venta.wait(5):
            return False, "El servidor no respondió, intenta de nuevo", None
        ok, mensaje, recibo_id = self.respuesta_venta
        if not ok:
            return False, mensaje, None
        nueva_venta.recibo_id = recibo_id       # lo asigna el servidor al guardar la venta
        ruta = nueva_venta.guardar_json()       # usa recibo_id para el nombre del archivo

        if self.codigo_cupon is not None:
            bd_cupones.usar_cupon(self.codigo_cupon)
        
        self.items.clear()  # vacia el carrito.
        self.cupon = 0.0
        self.codigo_cupon = None
        self.despacho = Despacho()  # la proxima compra parte con retiro en tienda
        if self.funcion_dibujar_tabla is not None:
            self.funcion_dibujar_tabla()
        return True, f"Recibo N°{nueva_venta.recibo_id}", ruta