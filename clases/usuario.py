class usuario:
    def __init__(self, nombre=None, password=None, rol="usuario", rut=None): # Definimos como predeterminado el rol 'usuario'  
        self.id = None                                                       
        self.nombre = nombre
        self.contrasena = password
        self.rol = rol
        self.rut = rut