from clases.producto import Producto
from clases.inventario import Inventario
from datos.bd import crear_tabla, mostrar_productos

# Crear la tabla si no existe
crear_tabla()

# Mostrar los productos
productos = mostrar_productos()
print(productos)