import sqlite3
import os
from datetime import datetime

ruta_bd = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ventas.db")


def conectar():
    return sqlite3.connect(ruta_bd)


def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cupones (
            codigo TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            valor INTEGER NOT NULL,
            fecha_venc TEXT NOT NULL,
            usos_maximos INTEGER NOT NULL,
            usos_actuales INTEGER DEFAULT 0
        )
    ''')
    conexion.commit()
    conexion.close()


def crear_cupon(codigo, tipo, valor, fecha_venc, usos_maximos):
    codigo = codigo.strip().upper()
    fecha_venc = fecha_venc.strip()

    if not codigo or not valor or not fecha_venc or not usos_maximos:
        return False, "Completa todos los campos del cupón."

    try:
        valor = int(valor)
        usos_maximos = int(usos_maximos)
    except ValueError:
        return False, "El valor y los usos máximos deben ser números enteros."

    if valor <= 0 or usos_maximos <= 0:
        return False, "El valor y los usos deben ser mayores a 0."

    if tipo == "porcentaje" and valor > 100:
        return False, "El porcentaje no puede ser mayor a 100%."

    try:
        fecha_dt = datetime.strptime(fecha_venc, "%d-%m-%Y").date()
    except ValueError:
        return False, "Formato de fecha inválido. Usa DD-MM-AAAA (ej: 31-12-2026)."

    if fecha_dt < datetime.now().date():
        return False, "La fecha de vencimiento ya pasó."

    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO cupones (codigo, tipo, valor, fecha_venc, usos_maximos, usos_actuales) VALUES (?, ?, ?, ?, ?, 0)",
        (codigo, tipo, valor, fecha_venc, usos_maximos)
    )
    conexion.commit()
    conexion.close()
    return True, f"El cupón {codigo} fue creado correctamente."


def buscar_cupon(codigo):
    crear_tabla()
    codigo = codigo.strip().upper()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT codigo, tipo, valor, fecha_venc, usos_maximos, usos_actuales FROM cupones WHERE codigo = ?",
        (codigo,)
    )
    fila = cursor.fetchone()
    conexion.close()

    if fila is None:
        return False, "El cupón ingresado no existe."

    tipo = fila[1]
    valor = fila[2]
    fecha_venc = fila[3]
    usos_maximos = fila[4]
    usos_actuales = fila[5]

    try:
        fecha_dt = datetime.strptime(fecha_venc, "%d-%m-%Y").date()
        if datetime.now().date() > fecha_dt:
            return False, "El cupón está vencido."
    except ValueError:
        pass

    if usos_actuales >= usos_maximos:
        return False, "El cupón ya alcanzó su límite de usos."

    return True, {"codigo": fila[0], "tipo": tipo, "valor": valor}


def usar_cupon(codigo):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE cupones SET usos_actuales = usos_actuales + 1 WHERE codigo = ?",
        (codigo.strip().upper(),)
    )
    conexion.commit()
    conexion.close()
