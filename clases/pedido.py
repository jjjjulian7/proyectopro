from datetime import datetime


class EstadoPedido:
    PENDIENTE = "Pendiente"
    EN_PREPARACION = "En preparación"
    DESPACHADO = "Despachado"
    ENTREGADO = "Entregado"
    CANCELADO = "Cancelado"

    # estado actual -> estados a los que puede pasar
    TRANSICIONES = {
        PENDIENTE: [EN_PREPARACION, CANCELADO],
        EN_PREPARACION: [DESPACHADO, CANCELADO],
        DESPACHADO: [ENTREGADO],
        ENTREGADO: [],
        CANCELADO: [],
    }

    # solo se restaura stock si se cancela antes de despachar
    CANCELABLES = [PENDIENTE, EN_PREPARACION]


class Pedido:
    def __init__(self, numero, venta_id, cliente, items):
        self.numero = numero
        self.venta_id = venta_id
        self.cliente = cliente
        self.items = [dict(item) for item in items]
        self.estado = EstadoPedido.PENDIENTE
        self.fecha = datetime.now().isoformat(timespec="seconds")
        self.historial = [(self.fecha, self.estado)]

    def puede_cambiar_a(self, nuevo_estado):
        return nuevo_estado in EstadoPedido.TRANSICIONES[self.estado]

    def cambiar_estado(self, nuevo_estado):
        if not self.puede_cambiar_a(nuevo_estado):
            return False, f"No se puede pasar de {self.estado} a {nuevo_estado}."
        self.estado = nuevo_estado
        self.historial.append((datetime.now().isoformat(timespec="seconds"), nuevo_estado))
        return True, f"Pedido N°{self.numero}: {self.estado}"

    def debe_restaurar_stock(self):
        """True si el pedido fue cancelado antes de ser despachado."""
        return self.estado == EstadoPedido.CANCELADO and \
            any(est == EstadoPedido.DESPACHADO for _, est in self.historial) is False

class FlujoPedido:
    """Orden normal que sigue un pedido y utilidades para consultarlo."""

    ORDEN = [
        EstadoPedido.PENDIENTE,
        EstadoPedido.EN_PREPARACION,
        EstadoPedido.DESPACHADO,
        EstadoPedido.ENTREGADO,
    ]
    FINALES = [EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO]

    DESCRIPCIONES = {
        EstadoPedido.PENDIENTE: "Recibimos tu compra y está esperando ser preparada.",
        EstadoPedido.EN_PREPARACION: "Estamos preparando los productos de tu pedido.",
        EstadoPedido.DESPACHADO: "Tu pedido ya salió de la tienda.",
        EstadoPedido.ENTREGADO: "Tu pedido fue entregado. ¡Gracias por tu compra!",
        EstadoPedido.CANCELADO: "El pedido fue cancelado.",
    }

    @classmethod
    def es_valido(cls, estado):
        return estado in EstadoPedido.TRANSICIONES

    @classmethod
    def es_final(cls, estado):
        return estado in cls.FINALES

    @classmethod
    def es_cancelable(cls, estado):
        return estado in EstadoPedido.CANCELABLES

    @classmethod
    def siguiente(cls, estado):
        """Siguiente estado del flujo normal o None si ya no hay más pasos."""
        if estado not in cls.ORDEN:
            return None
        posicion = cls.ORDEN.index(estado)
        if posicion + 1 >= len(cls.ORDEN):
            return None
        return cls.ORDEN[posicion + 1]

    @classmethod
    def progreso(cls, estado):
        """Porcentaje de avance (0 a 100). Un pedido cancelado marca 0."""
        if estado not in cls.ORDEN:
            return 0
        return int(cls.ORDEN.index(estado) * 100 / (len(cls.ORDEN) - 1))

    @classmethod
    def barra(cls, estado, ancho=10):
        """Barra de texto, por ejemplo [#####-----] para un pedido a medio camino."""
        llenos = round(cls.progreso(estado) * ancho / 100)
        return "[" + "#" * llenos + "-" * (ancho - llenos) + "]"

    @classmethod
    def descripcion(cls, estado):
        return cls.DESCRIPCIONES.get(estado, "Estado desconocido.")


class PanelPedidos:
    """Calcula los datos del panel del ADMIN a partir de {estado: [pedidos]}."""

    @staticmethod
    def contar(grupos):
        return {estado: len(lista) for estado, lista in grupos.items()}

    @staticmethod
    def total(grupos):
        return sum(len(lista) for lista in grupos.values())

    @staticmethod
    def activos(grupos):
        """Pedidos que todavía están en curso (ni entregados ni cancelados)."""
        return sum(len(lista) for estado, lista in grupos.items()
                   if not FlujoPedido.es_final(estado))

    @staticmethod
    def texto_resumen(grupos):
        lineas = ["PANEL DE PEDIDOS"]
        for estado, cantidad in PanelPedidos.contar(grupos).items():
            lineas.append(f"  {estado}: {cantidad}")
        lineas.append(f"  Total: {PanelPedidos.total(grupos)} "
                      f"(en curso: {PanelPedidos.activos(grupos)})")
        return "\n".join(lineas)


def formatear_historial(historial):
    """Convierte [(fecha, estado), ...] en un texto con un cambio por línea."""
    if not historial:
        return "Sin movimientos."
    return "\n".join(f"{fecha.replace('T', ' ')}  ->  {estado}" for fecha, estado in historial)


def tiempo_transcurrido(fecha_iso, ahora=None):
    """Texto corto tipo 'hace 5 min' a partir de una fecha ISO guardada en la BD."""
    try:
        fecha = datetime.fromisoformat(fecha_iso)
    except (TypeError, ValueError):
        return "fecha desconocida"
    segundos = int(((ahora or datetime.now()) - fecha).total_seconds())
    if segundos < 0:
        segundos = 0
    if segundos < 60:
        return "hace instantes"
    if segundos < 3600:
        return f"hace {segundos // 60} min"
    if segundos < 86400:
        return f"hace {segundos // 3600} h"
    return f"hace {segundos // 86400} d"