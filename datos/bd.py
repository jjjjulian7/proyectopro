import sqlite3

def conectar():
    conexion = sqlite3.connect('MaulenMarket_Productos.db') # Se conecta a la bd si no existe se crea sola
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
    producto.id = cursor.lastrowid #Te devuelve el id de el prud¿ducto agregado
    conexion.commit()
    conexion.close()

#JULIAN CORREA ACTUALIZAR PRODUCTO
def actualizar_producto(producto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''UPDATE productos SET nombre = ?, precio = ?, stock = ?, categoria = ? WHERE id = ?''',
                   (producto.nombre, producto.precio, producto.stock, producto.categoria, producto.id))
    conexion.commit()
    conexion.close()
    
#SEBASTIAN LEON 
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
    cursor.execute("SELECT SUM(precio * stock) FROM productos")
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

def filtrar_categoria(categoria):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos WHERE categoria = ?", (categoria,))
    productos = cursor.fetchall()
    conexion.close()
    return productos 

def promedio_precio_categoria(categoria):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT AVG(precio) FROM productos WHERE categoria = ?", (categoria,))
    promedio = cursor.fetchone()[0] # promedio = none 
    conexion.close()
    return promedio

def menor_stock(categoria):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos WHERE categoria = ? ORDER BY stock ASC LIMIT 1", (categoria,))
    productos = cursor.fetchone()
    conexion.close()
    return productos 


productos = mostrar_productos()
print(productos)