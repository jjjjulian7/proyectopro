import sqlite3

def conectar():
    conexion = sqlite3.connect('productos.db') # Se conecta a la bd si no existe se crea sola
    return conexion

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

def mostrar_productos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall() # Devuelve todas las filas encontradas
    # productos2 = cursor.fetchone() # Devuelve la primera fila encontrada
    conexion.close()
    return productos

productos = mostrar_productos()
print(productos)