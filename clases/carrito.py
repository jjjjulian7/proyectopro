import datos.bd as bd
from interfaz import Client_ProyProgV2 as ClienteRed
from tkinter import messagebox
from interfaz.abrir_carrito import abrir_carrito

class Carrito:
    def __init__(self):
        self.items = []
        self.funcion_dibujar_tabla = None  # Inicializamos la función como None
    
    def agregar_producto(self, producto, cantidad):
        print(f"Usuario : Agregando producto {producto.nombre}, Cantidad: {cantidad}" )
        ClienteRed.dato_envia({'type' : 'reservar_stock',
                               'id_producto' : producto.id,
                               'cantidad' : cantidad,
                               'nombre': producto.nombre }) #llama a la funcion reservar_stock de bd.py para reservar el stock del producto
        
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
        
    # funciones matemáticas para calcular el subtotal, iva y total del carrito        
    def calcular_subtotal(self):
        subtotal = 0
        for item in self.items:
            subtotal += item["precio"] * item["cantidad"]
        return subtotal
    
    def calcular_iva(self):
        subtotal = self.calcular_subtotal()
        return subtotal * 0.19  # 19% de IVA
    
    def calcular_total(self):
        return self.calcular_subtotal() + self.calcular_iva()    
    
    def vaciar_carrito(self):
        print("Usuario : Enviando solicitud al servidor para vaciar carrito")
        productos_a_devolver = []
        for item in self.items: # recorre los items del carrito y restaura el stock de cada producto en la base de datos
            productos_a_devolver.append({
                "id_producto": item["id"],
                "cantidad": item["cantidad"]
            })
        print(f"Productos a devolver stock: {productos_a_devolver}")
        ClienteRed.dato_envia({'type': 'vaciar_carrito', 'productos': productos_a_devolver})
    
    def procesar_respuesta_vaciar(self, ok, mensaje):
        if ok:
            self.items.clear()  # Vacía el carrito después de procesar la compra
            print("Carrito vaciado correctamente \n")
            messagebox.showinfo("Carrito vaciado", "El carrito ha sido vaciado correctamente.")
            if self.funcion_dibujar_tabla is not None:
                self.funcion_dibujar_tabla()  # Llama a la función para actualizar la interfaz
        else:
            messagebox.showwarning("Error al vaciar carrito", mensaje)
    
    def eliminar_producto(self, producto, cantidad):
        print("Soliciando eliminar producto)\n")
        ClienteRed.dato_envia({'type' : 'reponer_stock', 'id_producto' : producto["id"], 
                               'cantidad': cantidad})
        

    def procesar_respuesta_eliminar(self, ok, mensaje, cantidad, i, id_producto):
        if ok:            
            if cantidad <= 0:
                return
        
            if  cantidad > i["cantidad"]:
                cantidad = i["cantidad"]

            id_producto = i["id"]
            bd.restaurar_stock(id_producto, cantidad)

            i["cantidad"] -= cantidad

            if i["cantidad"] <= 0:
                self.items.remove(i)
                messagebox.showwarning("Producto eliminado del carrito")           
                if self.funcion_dibujar_tabla is not None:
                                self.funcion_dibujar_tabla()
        else:
            messagebox.showwarning("Error al eliminar producto", mensaje)

            
    def procesar_compra(self):
        if not self.items:
            return False, "El carrito está vacío"
        
        total = self.calcular_total()
        self.items.clear()  # Vacía el carrito después de procesar la compra
        return True, f"Compra procesada exitosamente. Total: ${total:.2f}"
    