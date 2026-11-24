import sqlite3
import os
from datetime import datetime
from clases.pedido import EstadoPedido

ruta_bd = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pedidos.db")


def conectar():
    return sqlite3.connect(ruta_bd)


def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            numero INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            cliente TEXT,
            estado TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedido_historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER NOT NULL,
            estado TEXT NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (numero) REFERENCES pedidos(numero)
        )
    ''')
    conexion.commit()
    conexion.close()


def _ahora():
    return datetime.now().isoformat(timespec="seconds")


def crear_pedido(venta_id, cliente):
    """Crea el pedido en estado Pendiente y devuelve su número."""
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    fecha = _ahora()
    cursor.execute(
        "INSERT INTO pedidos (venta_id, cliente, estado, fecha) VALUES (?, ?, ?, ?)",
        (venta_id, cliente, EstadoPedido.PENDIENTE, fecha)
    )
    numero = cursor.lastrowid
    cursor.execute(
        "INSERT INTO pedido_historial (numero, estado, fecha) VALUES (?, ?, ?)",
        (numero, EstadoPedido.PENDIENTE, fecha)
    )
    conexion.commit()
    conexion.close()
    return numero


def obtener_pedido(numero):
    """Devuelve (numero, venta_id, cliente, estado, fecha) o None."""
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT numero, venta_id, cliente, estado, fecha FROM pedidos WHERE numero = ?",
        (numero,)
    )
    fila = cursor.fetchone()
    conexion.close()
    return fila


def cambiar_estado(numero, nuevo_estado):
    """Valida la transición con EstadoPedido y la guarda. Devuelve (ok, mensaje)."""
    fila = obtener_pedido(numero)
    if fila is None:
        return False, "El pedido no existe."
    actual = fila[3]
    if nuevo_estado not in EstadoPedido.TRANSICIONES.get(actual, []):
        return False, f"No se puede pasar de {actual} a {nuevo_estado}."
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE pedidos SET estado = ? WHERE numero = ?", (nuevo_estado, numero))
    cursor.execute(
        "INSERT INTO pedido_historial (numero, estado, fecha) VALUES (?, ?, ?)",
        (numero, nuevo_estado, _ahora())
    )
    conexion.commit()
    conexion.close()
    return True, f"Pedido N°{numero}: {nuevo_estado}"


def listar_por_estado():
    """Para el panel del ADMIN: {estado: [(numero, venta_id, cliente, fecha), ...]}."""
    crear_tabla()
    grupos = {estado: [] for estado in EstadoPedido.TRANSICIONES}
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT numero, venta_id, cliente, estado, fecha FROM pedidos ORDER BY numero")
    for numero, venta_id, cliente, estado, fecha in cursor.fetchall():
        grupos[estado].append((numero, venta_id, cliente, fecha))
    conexion.close()
    return grupos


# ===========================================================================
# SEGUIMIENTO AMPLIADO DE PEDIDOS (se agrega sin tocar lo anterior)
# ===========================================================================
import datos.bd as bd_productos
import datos.bd_ventas as bd_ventas
from clases.pedido import FlujoPedido, PanelPedidos, formatear_historial, tiempo_transcurrido


def obtener_historial(numero):
    """Devuelve [(fecha, estado), ...] con todos los cambios del pedido, del más antiguo al más nuevo."""
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT fecha, estado FROM pedido_historial WHERE numero = ? ORDER BY id",
        (numero,)
    )
    historial = cursor.fetchall()
    conexion.close()
    return historial


def obtener_pedido_por_venta(venta_id):
    """Devuelve (numero, venta_id, cliente, estado, fecha) del pedido de esa venta o None."""
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT numero, venta_id, cliente, estado, fecha FROM pedidos WHERE venta_id = ?",
        (venta_id,)
    )
    fila = cursor.fetchone()
    conexion.close()
    return fila


def listar_por_cliente(cliente):
    """Todos los pedidos de un cliente, del más reciente al más antiguo."""
    crear_tabla()
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT numero, venta_id, cliente, estado, fecha FROM pedidos "
        "WHERE cliente = ? ORDER BY numero DESC",
        (cliente,)
    )
    pedidos = cursor.fetchall()
    conexion.close()
    return pedidos


def listar_activos():
    """Pedidos en curso (los que no están Entregados ni Cancelados)."""
    crear_tabla()
    finales = tuple(FlujoPedido.FINALES)
    marcas = ",".join("?" for _ in finales)
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        f"SELECT numero, venta_id, cliente, estado, fecha FROM pedidos "
        f"WHERE estado NOT IN ({marcas}) ORDER BY numero",
        finales
    )
    pedidos = cursor.fetchall()
    conexion.close()
    return pedidos


def contar_por_estado():
    """Devuelve {estado: cantidad} incluyendo los estados que tienen 0 pedidos."""
    return PanelPedidos.contar(listar_por_estado())


def avanzar_estado(numero):
    """Pasa el pedido al siguiente estado del flujo normal. Devuelve (ok, mensaje)."""
    fila = obtener_pedido(numero)
    if fila is None:
        return False, "El pedido no existe."
    siguiente = FlujoPedido.siguiente(fila[3])
    if siguiente is None:
        return False, f"El pedido N°{numero} ya está en estado final ({fila[3]})."
    return cambiar_estado(numero, siguiente)


def restaurar_stock(venta_id):
    """Devuelve al inventario las unidades de la venta. Retorna [(nombre, cantidad), ...] restauradas."""
    restaurados = []
    conexion = bd_productos.conectar()
    try:
        cursor = conexion.cursor()
        for id_producto, nombre, cantidad, _precio, _subtotal in bd_ventas.items_de_venta(venta_id):
            cursor.execute(
                "UPDATE productos SET stock = stock + ? WHERE id = ?",
                (cantidad, id_producto)
            )
            if cursor.rowcount > 0:  # si el producto fue eliminado del catálogo no hay nada que restaurar
                restaurados.append((nombre, cantidad))
        conexion.commit()
    except sqlite3.Error:
        conexion.rollback()
        raise
    finally:
        conexion.close()
    return restaurados


def cancelar_pedido(numero):
    """Cancela el pedido (solo antes de despachar) y restaura el stock. Devuelve (ok, mensaje)."""
    fila = obtener_pedido(numero)
    if fila is None:
        return False, "El pedido no existe."
    if not FlujoPedido.es_cancelable(fila[3]):
        return False, f"No se puede cancelar un pedido en estado {fila[3]}."
    ok, mensaje = cambiar_estado(numero, EstadoPedido.CANCELADO)
    if not ok:
        return False, mensaje
    try:
        restaurados = restaurar_stock(fila[1])
    except sqlite3.Error as error:
        return True, f"{mensaje}. Advertencia: no se pudo restaurar el stock ({error})."
    return True, f"{mensaje}. Stock restaurado en {len(restaurados)} producto(s)."


def detalle_pedido(numero):
    """Texto con el estado, el avance y el historial completo del pedido."""
    fila = obtener_pedido(numero)
    if fila is None:
        return "El pedido no existe."
    _numero, venta_id, cliente, estado, fecha = fila
    return "\n".join([
        f"Pedido N°{numero} (venta {venta_id}) - cliente: {cliente}",
        f"Estado: {estado} {FlujoPedido.barra(estado)} {FlujoPedido.progreso(estado)}%",
        FlujoPedido.descripcion(estado),
        f"Creado {tiempo_transcurrido(fecha)}",
        "Historial:",
        formatear_historial(obtener_historial(numero)),
    ])


def resumen_panel():
    """Texto listo para mostrar en el panel de pedidos del ADMIN."""
    return PanelPedidos.texto_resumen(listar_por_estado())