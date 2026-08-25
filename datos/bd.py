import sqlite3

def conectar():
    conexion = sqlite3.connect('productos_prueba.db') # Se conecta a la bd si no existe se crea sola
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
    cursor.execute('''INSERT INTO productos (nombre, precio, stock, categoria)
    VALUES (?, ?, ?, ?)''', (producto.nombre, producto.precio, producto.stock, producto.categoria ))
    producto.id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    
#SEBASTIAN LEON ELIMINAR PRODUCTO
def eliminar_producto(id_producto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''DELETE FROM productos WHERE id = ?''',(id_producto,))
    conexion.commit()
    conexion.close()
    ##cursor.lastrowid() ##recuperar id recien creada

#SEBASTIAN LEON TOTAL INVENTARIO
def calcular_total_inventario():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT SUM(precio * cantidad) FROM productos")
    total = cursor.fetchone()[0] # Devuelve el unico resultado, que es el total
    conexion.close

#SEBASTIAN LEON FILTRAR POR RANGO DE PRECIOS
def filtrar_rango_precios(min, max):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos WHERE precio BETWEEN ? AND ?", (min, max))
    productos = cursor.fetchall()
    conexion.close()
    return productos

productos = mostrar_productos()
print(productos)