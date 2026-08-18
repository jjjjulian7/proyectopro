import sqlite3

class bd:
    pass

def conectar():
    conexion = sqlite3.connect('productos.db') # Se conecta a la bd si no existe se crea sola
    return conexion
#JULIAN CORREA FUNCION CREAR TABLA
def crear_tabla():
    conexion = conectar() 
    cursor = conexion.cursor()   # Herramienta para hacer las consultas sql                   
    # Primare key autoincremente crea el id automaticamente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            categoria TEXT NOT NULL
        )
    ''')
    conexion.commit() # Guarda un cambio en la base datos a
    conexion.close() # Cierra la conexion a la base de datos
    # conexion.rollback() # Deshace un cambio en la base de datos


#JULIAN CORREA FUNCION MOSTRAR_PRODUCTOS
def mostrar_productos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall() # Devuelve todas las filas encontradas
    # productos2 = cursor.fetchone() # Devuelve la primera fila encontrada
    conexion.close()
    return productos
#JULIAN CORREA FUNCION INSERTAR_PRODUCTO
def insertar_producto(producto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''INSERT INTO productos (id , nombre, precio, stock, categoria)
    VALUES (?, ?, ?, ?, ?)''', (producto.id , producto.nombre, producto.precio, producto.stock, producto.categoria ))
    conexion.commit()
    conexion.close()
#SEBASTIAN LEON 
def eliminar_producto(id.producto):
    conexion= conectar()
    cursor = conexion.cursor()
    cursor.execute('''DELETE FROM productos WHERE id = ?''',(id.producto))
    conexion.commit()
    conexion.close()



productos = mostrar_productos()
print(productos)