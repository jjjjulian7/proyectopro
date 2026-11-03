from producto import *
import datos.bd as bd
class ListaDeseos:
    def __init__(self,nombreU):
        self.productos=[]
        self.nombre=nombreU


    def agregar_Lista(self,producto):
        self.productos.append({'nombre':producto.nombre,
                            'precio':producto.precio,
                            'stock':producto.stock,
                            'categoria':producto
                            })

