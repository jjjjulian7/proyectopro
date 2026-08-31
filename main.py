from clases.producto import Producto
from clases.inventario import Inventario
import datos.bd as bd
from datos.bd_usuarios import crear_admin_por_defecto

bd.crear_tabla()
crear_admin_por_defecto()

inventario = Inventario()

p = Producto("Mouse", 15000, 10, "Perifericos")

resultado = inventario.actualizar_producto(28, "Mouse editado" , 15000, 15, "Mouse")


print("Resultado:", resultado)
print("ID asignado:", p.id)
print("Productos en memoria:", inventario.productos)
print("Productos en BD:", bd.mostrar_productos())

inventario = Inventario()

for p in inventario.productos:
    print(p.id, p.nombre, p.precio, p.stock, p.categoria,)
    
print(inventario.validar_producto("Mouse editado" , 15000, 15, "Mouse"))