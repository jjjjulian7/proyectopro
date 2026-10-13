import tkinter as tk
from . import FuncionBotones as F
from . import estilo_boton
import tkinter.messagebox as messagebox
from clases import usuario 

# Paleta y fuentes (mismas del carrito)
COLOR_BORDE = "#dddddd"
COLOR_VERDE = "#5cb85c"
COLOR_TEXTO = "#222222"
COLOR_GRIS = "#777777"
FUENTE = ("Segoe UI", 10)
FUENTE_NEGRITA = ("Segoe UI", 10, "bold")

def ejecutar():
    # ventana de ingreso
    ventana = tk.Toplevel()
    ventana.title("MaulencitosMarket")
    ventana.geometry("1280x700")
    ventana.configure(bg="white")

    # Tarjeta centrada con borde fino
    tarjeta = tk.Frame(ventana, bg="white", highlightbackground=COLOR_BORDE, highlightthickness=1)
    tarjeta.place(relx=0.5, rely=0.5, anchor="center")

    contenido = tk.Frame(tarjeta, bg="white")
    contenido.pack(padx=50, pady=40)

    # Encabezado
    tk.Label(contenido, text="MaulencitosMarket", font=("Segoe UI", 26),
             bg="white", fg=COLOR_TEXTO, anchor="w").pack(fill="x")
    tk.Label(contenido, text="Inicia sesión o crea tu cuenta para continuar", font=FUENTE,
             bg="white", fg=COLOR_GRIS, anchor="w").pack(fill="x", pady=(2, 0))
    tk.Frame(contenido, bg=COLOR_BORDE, height=1).pack(fill="x", pady=(15, 20))

    # Campos
    tk.Label(contenido, text="Nombre Usuario", font=FUENTE_NEGRITA, bg="white",
             fg=COLOR_TEXTO, anchor="w").pack(fill="x")
    IngresoNombre = tk.Entry(
        contenido, width=34, font=FUENTE, relief="flat", bd=0,
        highlightthickness=1, highlightbackground=COLOR_BORDE, highlightcolor=COLOR_VERDE
    )
    IngresoNombre.pack(fill="x", ipady=6, pady=(4, 14))

    tk.Label(contenido, text="Clave Usuario", font=FUENTE_NEGRITA, bg="white",
             fg=COLOR_TEXTO, anchor="w").pack(fill="x")
    IngresoClave = tk.Entry(
        contenido, width=34, font=FUENTE, show="*", relief="flat", bd=0,
        highlightthickness=1, highlightbackground=COLOR_BORDE, highlightcolor=COLOR_VERDE
    )
    IngresoClave.pack(fill="x", ipady=6, pady=(4, 14))

    # botones,llamamos al archivo estilo_boton
    botones = tk.Frame(contenido, bg="white")
    botones.pack(fill="x", pady=(15, 0))
    botones.columnconfigure(0, weight=1, uniform="b")
    botones.columnconfigure(1, weight=1, uniform="b")

    boton_registrar = estilo_boton.crear_boton_verde(botones, "Registrar", lambda: F.registro(IngresoNombre, IngresoClave, ventana))
    boton_registrar.grid(row=0, column=0, sticky="ew", padx=(0, 6))

    boton_ingresar = estilo_boton.crear_boton_verde(botones, "Ingresar", lambda: F.ventana_usuario(ventana, IngresoNombre, IngresoClave))
    boton_ingresar.grid(row=0, column=1, sticky="ew", padx=(6, 0))