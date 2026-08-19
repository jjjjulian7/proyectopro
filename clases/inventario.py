import datos.bd as bd

class Inventario:
    def __init__(self):
        self.productos = []

#JULIAN CORREA FUNCION AGREGAR_PRODUCTO
def agregar_producto(self, p):
    self.productos.append(p)
    bd.insertar_producto()
    
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
def quitar_producto():
    id_producto = int(input("Ingrese el ID del producto a eliminar"))
    bd.eliminar_producto(id_producto)
            

