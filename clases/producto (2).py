class Producto:
    def __init__(self, id, nombre, precio, stock, categoria): # _init_ metodo para crear un objeto
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.categoria = categoria
    def mostrar_info(self): # self es como el this en java
        print("ID:", self.id)
        print("Nombre:", self.nombre)
        print("Precio:", self.precio)
        print("Stock:", self.stock)
        print("Categoría:", self.categoria)