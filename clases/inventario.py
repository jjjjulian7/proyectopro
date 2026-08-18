from datos.bd import bd


class Inventario:
    def __init__(self):
        self.productos = []

#JULIAN CORREA FUNCION AGREGAR_PRODUCTO
def agregar_producto(self, p):
    nuevo_producto = (p.id , p.nombre, p.nombre, p.precio, p.stock, p.categoria)
    self.productos.append(nuevo_producto)
    bd.insertar_producto()
#JULIAN CORREA FUNCION BUSCAR_PRODUCTO
def buscar_producto(self, nombre, id):
    print("Seleccione una opción de busqueda")    
    A = int(input("1 | Busqueda por id       2 | Busqueda por nombre"))
    if A == 1:
        id_search = int(input("Ingrese el id del producto"))
        for p in self.productos:
            if id_search == p.id:
                return p
    if A == 2:
        productos_buscados = []
        nombre_search = input("Ingrese el nombre del producto")
        for p in self.productos:
            if nombre_search.lower() in p.nombre.lower():
                productos_buscados.append(p)
        return productos_buscados
    
                
            

