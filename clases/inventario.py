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
            
#VALIDACIONES GENERALES       
    def validar_stock(self, stock):
        return stock >= 0
    
    def validar_precio(self, precio):
        return precio >= 0
    
    def validar_texto(self, texto):
        return texto.strip() != ""
    
    def validar_producto(self, nombre, precio, stock, categoria):
        if not self.validar_texto(nombre):
            return False
        if not self.validar_precio(precio):
            return False
        if not self.validar_stock(stock):
            return False 
        if not self.validar_texto(categoria):
            return False
        
        return True

#JULIAN CORREA FUNCION AGREGAR_PRODUCTO
    def agregar_producto(self, p):
        if not self.validar_producto(p.nombre, p.precio, p.stock, p.categoria):
            return False
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
        return None
    
    def actualizar_producto(self, id_producto, nombre, precio, stock, categoria):     
        for p in self.productos:
            if p.id == id_producto:
                if not self.validar_producto(nombre, precio, stock, categoria):
                    return False
                
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
            
