"""
datos/bd_cupones.py
Guarda y valida cupones en sqlite. El ADMIN los crea; el CLIENTE los aplica en su carrito.

IMPORTANTE: pon en RUTA_BD la MISMA ruta de base de datos que usan bd.py / bd_ventas.py,
para que el admin y el cliente lean la misma tabla.
"""
import sqlite3
from datetime import date, datetime

RUTA_BD = "ventas.db"   # <-- CAMBIAR por la ruta real que usas en bd_ventas.py

PORCENTAJE = "porcentaje"
MONTO_FIJO = "monto_fijo"


def _conectar():
    return sqlite3.connect(RUTA_BD)


def crear_tabla():
    with _conectar() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS cupones (
                codigo          TEXT PRIMARY KEY,
                tipo            TEXT NOT NULL CHECK (tipo IN ('porcentaje', 'monto_fijo')),
                valor           INTEGER NOT NULL CHECK (valor > 0),
                fecha_venc      TEXT NOT NULL,           -- AAAA-MM-DD
                usos_maximos    INTEGER NOT NULL CHECK (usos_maximos > 0),
                usos_actuales   INTEGER NOT NULL DEFAULT 0,
                activo          INTEGER NOT NULL DEFAULT 1
            )
        """)


def _parsear_fecha(texto):
    texto = (texto or "").strip()
    for formato in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    raise ValueError("Fecha inválida. Usa el formato DD-MM-AAAA (ej: 31-12-2026).")


# ---------------------------- ADMIN ----------------------------
def crear_cupon(codigo, tipo, valor, fecha_venc, usos_maximos):
    """Crea un cupón. Lanza ValueError con un mensaje claro si algo está mal."""
    codigo = (codigo or "").strip().upper()
    if not codigo:
        raise ValueError("Ingresa un código para el cupón.")
    if tipo not in (PORCENTAJE, MONTO_FIJO):
        raise ValueError("Tipo de cupón inválido.")
    try:
        valor = int(str(valor).strip())
        usos_maximos = int(str(usos_maximos).strip())
    except ValueError:
        raise ValueError("El valor y los usos máximos deben ser números enteros.")
    if valor <= 0:
        raise ValueError("El valor del descuento debe ser mayor que 0.")
    if tipo == PORCENTAJE and valor > 100:
        raise ValueError("Un porcentaje no puede ser mayor a 100.")
    if usos_maximos <= 0:
        raise ValueError("Los usos máximos deben ser al menos 1.")
    fecha = _parsear_fecha(fecha_venc)
    if fecha < date.today():
        raise ValueError("La fecha de vencimiento ya pasó.")

    crear_tabla()
    try:
        with _conectar() as con:
            con.execute(
                "INSERT INTO cupones (codigo, tipo, valor, fecha_venc, usos_maximos) VALUES (?, ?, ?, ?, ?)",
                (codigo, tipo, valor, fecha.isoformat(), usos_maximos),
            )
    except sqlite3.IntegrityError:
        raise ValueError(f"Ya existe un cupón con el código {codigo}.")
    return codigo


def listar_cupones():
    crear_tabla()
    with _conectar() as con:
        return con.execute(
            "SELECT codigo, tipo, valor, fecha_venc, usos_actuales, usos_maximos, activo FROM cupones ORDER BY codigo"
        ).fetchall()


def desactivar_cupon(codigo):
    with _conectar() as con:
        con.execute("UPDATE cupones SET activo = 0 WHERE codigo = ?", ((codigo or "").strip().upper(),))


# ---------------------------- CLIENTE ----------------------------
def obtener_cupon(codigo):
    crear_tabla()
    with _conectar() as con:
        fila = con.execute(
            "SELECT codigo, tipo, valor, fecha_venc, usos_maximos, usos_actuales, activo "
            "FROM cupones WHERE codigo = ?",
            ((codigo or "").strip().upper(),),
        ).fetchone()
    if fila is None:
        return None
    return {
        "codigo": fila[0], "tipo": fila[1], "valor": fila[2],
        "fecha_venc": date.fromisoformat(fila[3]),
        "usos_maximos": fila[4], "usos_actuales": fila[5], "activo": bool(fila[6]),
    }


def validar_cupon(codigo):
    """Devuelve (cupon_dict, '') si sirve, o (None, motivo) si no."""
    cupon = obtener_cupon(codigo)
    if cupon is None:
        return None, "El cupón no existe."
    if not cupon["activo"]:
        return None, "El cupón fue desactivado."
    if date.today() > cupon["fecha_venc"]:
        return None, "El cupón está vencido."
    if cupon["usos_actuales"] >= cupon["usos_maximos"]:
        return None, "El cupón está agotado."
    return cupon, ""


def registrar_uso(codigo):
    """Descuenta un uso de forma atómica. False si justo se agotó."""
    with _conectar() as con:
        cur = con.execute(
            "UPDATE cupones SET usos_actuales = usos_actuales + 1 "
            "WHERE codigo = ? AND activo = 1 AND usos_actuales < usos_maximos",
            ((codigo or "").strip().upper(),),
        )
        return cur.rowcount == 1


def calcular_descuento(cupon, base):
    """Monto en CLP (entero) a descontar sobre 'base'. Nunca supera la base."""
    if cupon is None:
        return 0
    if cupon["tipo"] == PORCENTAJE:
        monto = int(round(base * cupon["valor"] / 100))
    else:
        monto = int(cupon["valor"])
    return min(monto, int(base))
