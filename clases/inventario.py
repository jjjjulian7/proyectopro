import datos.bd as bd

class Inventario:
    def __init__(self):
        self.productos = []

#JULIAN CORREA FUNCION AGREGAR_PRODUCTO
def agregar_producto(self, p):
    for producto in self.productos:
        if producto.id == p.id:
            return False
    
    self.productos.append(p)
    bd.insertar_producto()
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
    
#SEBASTIAN LEON 
def quitar_producto(self, id_producto):
    #id_producto = int(input("Ingrese el ID del producto a eliminar")) ##mandarlo al main los inputs
    for p in self.productos:
        if p.id == id_producto:
            self.productos.remove(p)
            bd.eliminar_producto(id_producto)
            return True
            

