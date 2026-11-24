from datos import bd_deseos


class Notificacion:
    
    def __init__(self, rut, id_producto, mensaje):
        self.rut = rut
        self.id_producto = id_producto
        self.mensaje = mensaje

    def guardar(self):
        bd_deseos.guardar_notificacion(self.rut, self.id_producto, self.mensaje)

    @staticmethod
    def de_usuario(rut):
        return [Notificacion(rut, id_p, texto) for id_p, texto in bd_deseos.listar_notificaciones(rut)]


class Suscripcion:
    
    def __init__(self, rut, id_producto):
        self.rut = rut
        self.id_producto = id_producto

    def guardar(self):
        """True si se creo, False si ya estaba suscrito."""
        return bd_deseos.agregar_suscripcion(self.id_producto, self.rut)

    @staticmethod
    def de_usuario(rut):
        return [Suscripcion(rut, id_p) for (id_p,) in bd_deseos.listar_suscripciones(rut)]

    @staticmethod
    def ruts_de_producto(id_producto):
        return bd_deseos.suscritos_a_producto(id_producto)

    @staticmethod
    def contar_por_producto():
        return bd_deseos.contar_suscritos_por_producto()


class ListaDeseos:
    
    def __init__(self, rut):
        self.rut = rut

    def agregar(self, id_producto, precio):
        
        return bd_deseos.agregar_deseo(id_producto, self.rut, precio)

    def quitar(self, id_producto):
        return bd_deseos.quitar_deseo(id_producto, self.rut)

    def items(self):
        
        return bd_deseos.listar_deseos(self.rut)

    @staticmethod
    def ruts_con_deseo(id_producto):
        return bd_deseos.ruts_con_deseo(id_producto)