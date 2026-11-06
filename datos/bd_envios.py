import sqlite3 , os
ruta_bd = os.path.join(os.path.dirname(os.path.dirname(__file__)), "envios.db")  # envios.db en la raiz del proyecto

def conectar():
    conexion = sqlite3.connect(ruta_bd) # Se conecta a la bd si no existe se crea sola
    return conexion

REGIONES = [
    "Arica y Parinacota", "Tarapacá", "Antofagasta", "Atacama", "Coquimbo",
    "Valparaíso", "Región Metropolitana", "O'Higgins", "Maule", "Ñuble",
    "Biobío", "La Araucanía", "Los Ríos", "Los Lagos", "Aysén", "Magallanes",
]

# Valores Iniciales, el adimn las puede cambiar luego en su ventana
COSTO_REGION_ORIGEN = 4000
COSTO_METROPOLITANA = 6000
COSTO_RESTO = 8000

DIAS_REGION_ORIGEN = 2
DIAS_RESTO = 5

MONTO_MINIMO_INICIAL = 100000
REGION_ORIGEN_INICIAL = "Maule"


def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()

    # Tabla que guarda los datos de envios 
    cursor.execute('''                              
        CREATE TABLE IF NOT EXISTS envios (
            region TEXT PRIMARY KEY,
            costo REAL NOT NULL (costo >= 0),
            dias_habiles INTEGER NOT NULL CHECK (dias_habiles >= 0)
        )
    ''')
    
    # Tabla que guarda el monto minimo para envio gratis
    cursor.execute('''                              
        CREATE TABLE IF NOT EXISTS config_envio( 
            id INTEGER PRIMARY KEY CHECK (id = 1),
            monto_minimo REAL NOT NULL DEFAULT '100000',
            region_tienda TEXT NOT NUL DEFAULT 'Maule'
                   
        )
    ''')    #  Garantiza que solo haya una fila en la tabla 

    # DAtos iniciales, solo agrega si las tablas estan vacias, no cambia lo que el admin haya hecho
    cursor.execute("SELECT COUNT(*) FROM envios")
    if cursor.fetchone()[0] == 0:
        for region in REGIONES:
            if region == REGION_ORIGEN_INICIAL:
                costo, dias = COSTO_REGION_ORIGEN, DIAS_REGION_ORIGEN
            elif region == "Región Metropolitana":
                costo, dias = COSTO_METROPOLITANA, DIAS_RESTO
            else:
                costo, dias = COSTO_RESTO, DIAS_RESTO
            cursor.execute("INSERT INTO envios (region, costo, dias_habiles) VALUES (?, ?, ?)",
                           (region, costo, dias))
 
    cursor.execute("INSERT OR IGNORE INTO config_envio (id, monto_minimo, region_tienda) VALUES (1, ?, ?)",
                   (MONTO_MINIMO_INICIAL, REGION_ORIGEN_INICIAL))
 

    conexion.commit()
    conexion.close()


# FUNCIONES TABLA ENVIOS:
def guardar_tarifa(region, costo, dias_habiles):  # actualiza la tarifa de una region
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO envios (region, costo, dias_habiles)
        VALUES (?, ?, ?)
    ''', (region, costo, dias_habiles))
    conexion.commit()
    conexion.close()

def listar_tarifas():                           # Devuelve las tuplas, ordenadas por region
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT region, costo, dias_habiles FROM envios ORDER BY region")
    filas = cursor.fetchall()
    conexion.close
    return filas


def obtener_tarifa(region):                     # Devuelve la tupla de una region
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT region, costo, dias_habiles FROM envios WHERE region = ?", (region,))
    fila = cursor.fetchone()
    conexion.close()
    return fila


# FUNCIONES TABLA CONFIG:
def insertar_monto(monto):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO config_envio (id, monto_minimo) 
    ''')

