import datos.bd as bd

class Carrito:
    def __init__(self):
        self.items = []
        
    def agregar_producto(self, producto, cantidad):
        for item in self.items: #recorre los items del carrito y si el producto ya existe, aumenta la cantidad
            if item["id"] == producto.id: #compara el id del producto con los items del carrito
                item["cantidad"] += cantidad
                return True
        self.items.append({ #agrega un nuevo producto al carrito si no existe
            "id": producto.id, # se agrega id para identificar el producto mas facil 
            "nombre": producto.nombre,
            "precio": producto.precio,
            "cantidad": cantidad
        })
        return True
    
    def vaciar_carrito(self):
        for item in self.items: # recorre los items del carrito y restaura el stock de cada producto en la base de datos
            id_producto = item["id"] #toma el id del producto del item del carrito para buscarlo en la base de datos y restaurar el stock
            cantidad = item["cantidad"] 
            bd.restaurar_stock(id_producto, cantidad) #funcion bd
        self.items.clear() # clear vacía la lista de items del carrito
    
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