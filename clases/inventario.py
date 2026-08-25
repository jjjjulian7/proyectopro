import datos.bd as bd

class Inventario:
    def __init__(self):
        self.productos = []

#JULIAN CORREA FUNCION AGREGAR_PRODUCTO
def agregar_producto(self, p):
    bd.insertar_producto()
    self.productos.append(p)
    return True
    
#JULIAN CORREA FUNCION BUSCAR_PRODUCTO
def buscar_producto(self, opcion, valor):
    
    if opcion == 1:
        for p in self.productos:
            if p.id == valor:
                return p
    elif opcion == 2:
        productos_buscados = []
        for p in self.productos:
            if valor.lower() in p.nombre.lower():
                productos_buscados.append(p)
        return productos_buscados
    return None

#JULIAN CORREA VALIDAR STOCK
def validar_stock(self, stock):
    return stock >= 0

#JULIAN CORREA ACTUALIZAR PRODUCTO
def actualizar_producto(self, id_producto, nombre, precio, stock, categoria):

    if not self.validar_stock(stock):
        return False

    for p in self.productos:
        if p.id == id_producto:
            p.nombre = nombre
            p.precio = precio
            p.stock = stock
            p.categoria = categoria

            bd.actualizar_producto(p)
            return True
    return False

#SEBASTIAN LEON QUITAR_PRODUCTO
def quitar_producto(self, id_producto):
    #id_producto = int(input("Ingrese el ID del producto a eliminar")) ##mandarlo al main los inputs
    for p in self.productos:
        if p.id == id_producto:
            self.productos.remove(p)
            bd.eliminar_producto(id_producto)
            return True
            
def filtrar_categoria(self, categoria):
    productos_filtrados = []
    for p in self.productos :
        if p.categoria.lower == categoria.lower:
            productos_filtrados.append(p)
    return productos_filtrados


