import datos.bd as bd
from clases.producto import Producto

class Inventario:
    def __init__(self):
        self.productos = []
        
        filas = bd.mostrar_productos()
        
        for fila in filas:
            p = Producto(fila[1], fila[2], fila[3], fila[4])
            p.id = fila[0]
            self.productos.append(p)

#JULIAN CORREA FUNCION AGREGAR_PRODUCTO
    def agregar_producto(self, p):
        bd.insertar_producto(p)
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
    
    def actualizar_producto(self, id_producto, nombre, precio, stock, categoria):
        for p in self.productos:
            if p.id == id_producto:
                p.nombre = nombre
                p.precio = precio
                p.stock = stock
                p.categoria = categoria

                bd.actualizar_producto(p)
                return True

        return False
    
#SEBASTIAN LEON 
    def quitar_producto(self, id_producto):
        #id_producto = int(input("Ingrese el ID del producto a eliminar")) ##mandarlo al main los inputs
        for p in self.productos:
            if p.id == id_producto:
                self.productos.remove(p)
                bd.eliminar_producto(id_producto)
                return True
            
