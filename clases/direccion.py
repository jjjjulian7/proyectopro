class Direccion:
    # datos de quien recibe y a donde se despacha
    def __init__(self, destinatario="", calle="", comuna="", region=""):
        self.destinatario = (destinatario or "").strip()
        self.calle = (calle or "").strip()
        self.comuna = (comuna or "").strip()
        self.region = (region or "").strip()

    # devuelve (ok, mensaje) y revisa que no falte nada y que la region tenga tarifa
    def validar(self, regiones_validas):
        if not self.destinatario:
            return False, "Ingresa el nombre de quien recibe."
        if not self.calle:
            return False, "Ingresa la dirección de entrega."
        if not self.comuna:
            return False, "Ingresa la comuna."
        if not self.region:
            return False, "Selecciona la región."
        if self.region not in regiones_validas:
            return False, f"No hay tarifa de envío configurada para la región '{self.region}'."
        return True, ""

    def a_diccionario(self):
        return {"destinatario": self.destinatario, "direccion": self.calle,
                "comuna": self.comuna, "region": self.region}

    def __str__(self):
        return f"{self.calle}, {self.comuna}, {self.region}"
