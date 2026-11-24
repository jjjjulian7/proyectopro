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
COSTO_REGION_ORIGEN = 4990      # valores del enunciado del hito 3
COSTO_METROPOLITANA = 5990
COSTO_RESTO = 7990

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
            costo REAL NOT NULL CHECK (costo >= 0),
            dias_habiles INTEGER NOT NULL CHECK (dias_habiles >= 0)
        )
    ''')
    
    # Tabla que guarda el monto minimo para envio gratis
    cursor.execute('''                              
        CREATE TABLE IF NOT EXISTS config_envio( 
            id INTEGER PRIMARY KEY CHECK (id = 1),
            monto_minimo REAL NOT NULL DEFAULT '100000' CHECK (monto_minimo >= 0),
            region_tienda TEXT NOT NULL DEFAULT 'Maule'
                   
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
    if region not in REGIONES:  # Validamos los datos ingresados
        raise ValueError("Selecciona una region valida")
    try:
        costo = int(str(costo).strip())
        dias_habiles = int(str(dias_habiles).strip())
    except ValueError:
        raise ValueError("Ingrese numero enteros")
    if costo < 0:   
        raise ValueError("El costo no puede ser negativo")
    if dias_habiles<0:
        raise ValueError("Los dias habiles no pueden ser negativos")
    
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
    conexion.close()
    return filas


def obtener_tarifa(region):                     # Devuelve la tupla de una region
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    fila = cursor.execute("SELECT region, costo, dias_habiles FROM envios WHERE region = ?", (region,)).fetchone()
    conexion.close()
    return fila


# lista con los nombres de las regiones que tienen tarifa
def regiones_con_tarifa():
    return [fila[0] for fila in listar_tarifas()]


# FUNCIONES TABLA CONFIG:
# devuelve (monto_minimo, region_tienda)
def obtener_config():
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    fila = cursor.execute("SELECT monto_minimo, region_tienda FROM config_envio WHERE id = 1").fetchone()
    conexion.close()
    return fila


# monto desde el cual el envio sale gratis y region donde esta la tienda
def guardar_config(monto_minimo, region_tienda):
    try:
        monto_minimo = int(str(monto_minimo).strip())
    except ValueError:
        raise ValueError("El monto minimo debe ser un numero entero")
    if monto_minimo < 0:
        raise ValueError("El monto minimo no puede ser negativo")
    if region_tienda not in REGIONES:
        raise ValueError("Selecciona la region de la tienda")

    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT OR REPLACE INTO config_envio (id, monto_minimo, region_tienda) VALUES (1, ?, ?)",
                   (monto_minimo, region_tienda))
    conexion.commit()
    conexion.close()
