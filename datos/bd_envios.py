import sqlite3 , os
ruta_bd = os.path.join(os.path.dirname(os.path.dirname(__file__)), "envios.bd")  # envios.db en la raiz del proyecto

def conectar():
    conexion = sqlite3.connect(ruta_bd) # Se conecta a la bd si no existe se crea sola
    return conexion

def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()

    # Tabla que guarda los datos de envios 
    cursor.execute('''                              
        CREATE TABLE IF NOT EXISTS envios (
            region TEXT PRIMARY KEY,
            costo REAL NOT NULL,
            dias_habiles INTEGER NOT NULL
        )
    ''')
    
    # Tabla que guarda el monto minimo para envio gratis
    cursor.execute('''                              
        CREATE TABLE IF NOT EXISTS config_envio( 
            id INTEGER PRIMARY KEY DEFAULT 1,
            monto_minimo REAL NOT NULL DEFAULT 'activo',

            CONSTRAINT unica_fila CHECK (id = 1)        
        )
    ''')    #  Garantiza que solo haya una fila en la tabla 



# FUNCIONES TABLA ENVIOS:
def insertar_envio(envio):  
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO envios (region, costo, dias_habiles)
        VALUES (?, ?, ?)
    ''', (envio.region, envio.costo, envio.dias_habiles))
    conexion.commit()
    conexion.close()




# FUNCIONES TABLA CONFIG:
def insertar_monto(monto):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO config_envio (id, monto_minimo) 
    ''')

