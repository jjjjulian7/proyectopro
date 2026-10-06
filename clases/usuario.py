import sqlite3

class usuario:
    def __init__(self, nombre=None, password=None, rol="usuario", rut=None): # Definimos como predeterminado el rol de usuario
        self.id = None                                                       
        self.nombre = nombre
        self.contrasena = password
        self.rol = rol
        self.rut = rut

    def guardar_en_bd(self):
        from datos import bd_usuarios as bd  # import dentro del método para evitar import circular

        if bd.buscar_usuario(self.nombre) is not None:
            return False  # el nombre ya existe

        bd.insertar_usuario(self)
        return True

    @staticmethod
    def validar_credenciales(nombre, clave):
        from datos import bd_usuarios as bd

        fila = bd.buscar_usuario(nombre)
        if fila is None:
            return None

        # orden de columnas en la tabla: id, nombre, rut, contrasena, rol
        _, nombre_bd, rut_bd, contrasena_bd, rol_bd = fila

        if contrasena_bd == clave:
            return usuario(nombre=nombre_bd, password=contrasena_bd, rol=rol_bd, rut=rut_bd)

        return None