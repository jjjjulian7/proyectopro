from datetime import date, timedelta


class TarifaEnvio:
    """Tarifa de envio de una region: costo en CLP y dias habiles de entrega."""

    def __init__(self, region, costo, dias_habiles):
        self.region = region
        self.costo = costo
        self.dias_habiles = dias_habiles


class Despacho:
    """Modalidad de entrega del carrito: retiro en tienda (gratis) o despacho a domicilio."""

    RETIRO = "Retiro en tienda"
    DOMICILIO = "Despacho a domicilio"

    def __init__(self, modalidad=RETIRO, direccion=None, tarifa=None, monto_minimo=0):
        self.modalidad = modalidad
        self.direccion = direccion          # objeto Direccion (clases/direccion.py), solo a domicilio
        self.tarifa = tarifa                # objeto TarifaEnvio de la region elegida
        self.monto_minimo = monto_minimo    # desde este monto el envio es gratis

    def es_retiro(self):
        return self.modalidad != Despacho.DOMICILIO

    def calcular_costo(self, subtotal_neto):
        """Costo de envio en CLP. 0 si es retiro, si no hay tarifa, si el carrito esta vacio
        o si el subtotal neto alcanza el monto minimo de envio gratis."""
        if self.es_retiro() or self.tarifa is None or subtotal_neto <= 0:
            return 0
        if self.monto_minimo and subtotal_neto >= self.monto_minimo:
            return 0
        return int(round(self.tarifa.costo))

    def fecha_estimada(self, desde=None):
        """Fecha de entrega estimada (suma dias habiles, sin sabados ni domingos). None si es retiro."""
        if self.es_retiro() or self.tarifa is None:
            return None
        fecha = desde or date.today()
        faltan = int(self.tarifa.dias_habiles)
        while faltan > 0:
            fecha += timedelta(days=1)
            if fecha.weekday() < 5:     # 0-4 = lunes a viernes
                faltan -= 1
        return fecha

    def a_diccionario(self, costo_envio, desde=None):
        """Formato que viaja por socket, se guarda en la BD y sale en el comprobante."""
        fecha = self.fecha_estimada(desde)
        datos = {"modalidad": self.modalidad,
                 "costo_envio": costo_envio,
                 "fecha_entrega": fecha.isoformat() if fecha else None,
                 "destinatario": None, "direccion": None, "comuna": None, "region": None}
        if not self.es_retiro() and self.direccion is not None:
            datos.update(self.direccion.a_diccionario())
        return datos