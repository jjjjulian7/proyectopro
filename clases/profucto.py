class Producto:
    def __init__(self, id, nombre, precio, stock, categoria):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.categoria = categoria
    def mostrar_info(self):
        print(self.id, self.nombre, self.precio)