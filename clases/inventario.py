import datos.bd as bd
from clases.producto import Producto

class Inventario:
    def __init__(self):
        self.productos = []
        
        filas = bd.mostrar_productos()
        
        # Recorre las filas de la base de datos y crea objetos Producto para cada fila
        for fila in filas: #ingresa los productos de la base de datos a la lista de productos del inventario
            p = Producto(fila[1], fila[2], fila[3], fila[4]) #fila[0] es el id, fila[1] es el nombre, fila[2] es el precio, fila[3] es el stock, fila[4] es la categoria
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
        if not self.validar_producto(p.nombre, p.precio, p.stock, p.categoria): # revisa que los datos del producto sean válidos antes de agregarlo
            return False
        bd.insertar_producto(p)
        self.productos.append(p)
        return True

#JULIAN CORREA FUNCION BUSCAR_PRODUCTO
    def buscar_producto(self, opcion, valor): #Recibe el valor a buscar y la opcion de busqueda (1 por id, 2 por nombre o categoria)
    
        if opcion == 1:
            for p in self.productos:
                if p.id == valor:
                    return p
        elif opcion == 2:
            productos_buscados = []
            terminos = valor.lower().split()
            for p in self.productos:
                texto_producto = f"{p.nombre} {p.categoria}".lower()
                if all(termino in texto_producto for termino in terminos): #all verifica que todos los términos de búsqueda estén presentes en el nombre o categoría del producto
                    productos_buscados.append(p)
            return productos_buscados
        return None
    
    def actualizar_producto(self, id_producto, nombre, precio, stock, categoria):     
        for p in self.productos:
            if p.id == id_producto:
                if not self.validar_producto(nombre, precio, stock, categoria): # busca el producto por id y valida los nuevos datos antes de actualizar
                    return False
                
                p.nombre = nombre #datos nuevos al producto
                p.precio = precio
                p.stock = stock
                p.categoria = categoria

                bd.actualizar_producto(p)
                return True

        return False
    
#SEBASTIAN LEON 
    def quitar_producto(self, id_producto):
        for p in self.productos:
            if p.id == id_producto:
                self.productos.remove(p)
                bd.eliminar_producto(id_producto)
                return True
        return False
            
