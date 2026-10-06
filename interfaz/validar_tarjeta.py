import tkinter as tk
from tkinter import messagebox
from datetime import date

##Codigo reutilizado de un commit anterior, mejorando la interfaz solamente

FUENTE = ("Segoe UI", 10)
FUENTE_NEGRITA = ("Segoe UI", 10, "bold")
COLOR_VERDE = "#5cb85c"
COLOR_NARANJA = "#eeac57"

PREFIJO_TARJETA = "4345"
LARGO_TARJETA = 16
LARGO_CVV = 3


def solo_digitos(texto):
    """True si el texto no está vacío y todos sus caracteres son 0-9."""
    if texto == "":
        return False
    for c in texto:
        if c not in "0123456789":
            return False
    return True


def abrir_validar_tarjeta(padre, total, carrito=None):
    """Ventana de validación de tarjeta.

    padre:   ventana del carrito (se cierra junto con esta al pagar)
    total:   monto a pagar
    carrito: instancia de Carrito (opcional)
    """
    ventana = tk.Toplevel(padre)
    ventana.title("Validar tarjeta")
    ventana.geometry("400x430")
    ventana.resizable(False, False)
    ventana.configure(bg="white")

    ventana.transient(padre)
    ventana.wait_visibility()
    ventana.grab_set()
    ventana.focus_set()

    tk.Label(
        ventana, text=f"Total a pagar: ${total:,.0f} CLP",
        font=("Segoe UI", 13, "bold"), bg="white", fg="#1b5e20"
    ).pack(pady=(20, 15))

    form = tk.Frame(ventana, bg="white")
    form.pack(fill="x", padx=30)

    # Número de tarjeta
    tk.Label(form, text="Número de tarjeta (16 dígitos, sin espacios)",
             font=FUENTE, bg="white", anchor="w").pack(fill="x")
    ent_numero = tk.Entry(form, font=FUENTE, relief="solid", bd=1)
    ent_numero.pack(fill="x", pady=(2, 12), ipady=3)

    # Fecha de vencimiento: mes y año en campos distintos
    tk.Label(form, text="Fecha de vencimiento",
             font=FUENTE, bg="white", anchor="w").pack(fill="x")
    fila_fecha = tk.Frame(form, bg="white")
    fila_fecha.pack(fill="x", pady=(2, 12))

    tk.Label(fila_fecha, text="Mes (MM)", font=FUENTE, bg="white").pack(side="left")
    ent_mes = tk.Entry(fila_fecha, font=FUENTE, width=4, relief="solid", bd=1)
    ent_mes.pack(side="left", padx=(5, 20), ipady=3)

    tk.Label(fila_fecha, text="Año (AAAA)", font=FUENTE, bg="white").pack(side="left")
    ent_anio = tk.Entry(fila_fecha, font=FUENTE, width=6, relief="solid", bd=1)
    ent_anio.pack(side="left", padx=5, ipady=3)

    # CVV
    tk.Label(form, text="CVV (3 dígitos)",
             font=FUENTE, bg="white", anchor="w").pack(fill="x")
    ent_cvv = tk.Entry(form, font=FUENTE, width=6, show="*", relief="solid", bd=1)
    ent_cvv.pack(anchor="w", pady=(2, 12), ipady=3)

    def error(mensaje, campo):
        messagebox.showerror("Error", mensaje, parent=ventana)
        campo.focus_set()

    def validar():
        numero = ent_numero.get().strip()
        mes_txt = ent_mes.get().strip()
        anio_txt = ent_anio.get().strip()
        cvv = ent_cvv.get().strip()

        #numero de tarjeta
        if not solo_digitos(numero):
            error("El número de tarjeta solo puede contener números.", ent_numero)
            return
        if len(numero) != LARGO_TARJETA:
            error(f"El número de tarjeta debe tener exactamente {LARGO_TARJETA} dígitos.",
                  ent_numero)
            return
        if numero[:4] != PREFIJO_TARJETA:
            error(f"El número de tarjeta debe comenzar con {PREFIJO_TARJETA}.", ent_numero)
            return

        # mes
        if not solo_digitos(mes_txt):
            error("El mes debe ser un número.", ent_mes)
            return
        mes = int(mes_txt)
        if mes < 1 or mes > 12:
            error("El mes debe estar entre 1 y 12.", ent_mes)
            return

        # año
        if not solo_digitos(anio_txt):
            error("El año debe ser un número.", ent_anio)
            return
        if len(anio_txt) != 4:
            error("El año debe tener 4 dígitos (ejemplo: 2028).", ent_anio)
            return
        anio = int(anio_txt)

        # vencimiento de tarjeta
        hoy = date.today()
        if anio < hoy.year:
            error("La tarjeta está vencida.", ent_anio)
            return
        if anio == hoy.year and mes < hoy.month:
            error("La tarjeta está vencida.", ent_mes)
            return

        # cvv
        if not solo_digitos(cvv):
            error("El CVV solo puede contener números.", ent_cvv)
            return
        if len(cvv) != LARGO_CVV:
            error(f"El CVV debe tener exactamente {LARGO_CVV} dígitos.", ent_cvv)
            return

        # ---- Todo correcto: cierra esta ventana y el carrito ----
        messagebox.showinfo("Pagos", "Pago realizado con éxito.", parent=ventana)
        ventana.destroy()
        padre.destroy()

    def cancelar():
        ventana.destroy()

    botones = tk.Frame(ventana, bg="white")
    botones.pack(fill="x", padx=30, pady=(10, 0))

    tk.Button(
        botones, text="Cancelar", font=FUENTE,
        bg=COLOR_NARANJA, fg="white", activebackground="#d99a45",
        activeforeground="white", relief="flat", bd=0,
        padx=12, pady=5, cursor="hand2", command=cancelar
    ).pack(side="left")

    tk.Button(
        botones, text="Pagar", font=FUENTE,
        bg=COLOR_VERDE, fg="white", activebackground="#4cae4c",
        activeforeground="white", relief="flat", bd=0,
        width=12, pady=5, cursor="hand2", command=validar
    ).pack(side="right")

    ent_numero.focus_set()
    return ventana