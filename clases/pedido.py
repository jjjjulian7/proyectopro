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