import os
import tkinter as tk
from . import estilo_boton
from . import FuncionBotones as F
import threading
import Server_ProgProyV2 as ServidorRed

#misma paleta q use en el carrito (copiada)
COLOR_FONDO = "#f4f6f8"
COLOR_TARJETA = "white"
COLOR_BORDE = "#dddddd"
COLOR_TEXTO = "#222222"
COLOR_SUAVE = "#777777"
COLOR_VERDE = "#5cb85c"
COLOR_MORADO= "#7422A8"
FUENTE = ("Segoe UI", 11)
FUENTE_NEGRITA = ("Segoe UI", 10, "bold")

#por defecto busca  proyectopro/imagenes/logo.png
LOGO_RUTA = os.path.join(os.path.dirname(__file__), "..", "imagenes", "logo.png")
ALTO_LOGO = 120  # alto máximo en píxeles


def _cargar_logo():
    """Devuelve la imagen del logo, o None si no se encuentra."""
    try:
        img = tk.PhotoImage(file=LOGO_RUTA)
        if img.height() > ALTO_LOGO:
            img = img.subsample(max(1, img.height() // ALTO_LOGO))
        return img
    except tk.TclError:
        return None


def _campo(tarjeta, fila, texto, **opciones):
    """Etiqueta + campo de texto con borde que se marca en verde al enfocar."""
    tk.Label(tarjeta, text=texto, font=FUENTE_NEGRITA, bg=COLOR_TARJETA,
             fg=COLOR_TEXTO, anchor="w").grid(row=fila, column=0, sticky="w",
                                              pady=(14, 4))
    entrada = tk.Entry(
        tarjeta, font=FUENTE, width=30, relief="flat", bd=0,
        bg="#fafafa", fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO,
        highlightthickness=1, highlightbackground=COLOR_BORDE,
        highlightcolor=COLOR_VERDE, **opciones)
    entrada.grid(row=fila + 1, column=0, sticky="ew", ipady=7)
    return entrada


def abrir_ventana_funcionario():
    # ventana de ingreso
    ventana = tk.Tk()
    ventana.title("MaulencitosMarketLoginADMIN")
    ventana.geometry("1280x700")
    hilo_server = threading.Thread(target=ServidorRed.iniciar_servidor)
    hilo_server.daemon = True
    hilo_server.start()
    ventana.configure(bg=COLOR_FONDO)

    # Logo arriba del todo, centrado
    logo = _cargar_logo()
    if logo is not None:
        lbl_logo = tk.Label(ventana, image=logo, bg=COLOR_FONDO)
        lbl_logo.image = logo  # evita que Python borre la imagen
    else:
        # Si no se encuentra el archivo, muestra el nombre en texto
        lbl_logo = tk.Label(ventana, text="MaulencitosMarket",
                            font=("Segoe UI", 28, "bold"),
                            bg=COLOR_FONDO, fg=COLOR_VERDE)
    lbl_logo.pack(side="top", pady=(40, 0))

    # Tarjeta centrada
    tarjeta = tk.Frame(ventana, bg=COLOR_TARJETA, highlightthickness=1,
                       highlightbackground=COLOR_BORDE, padx=50, pady=40)
    tarjeta.place(relx=0.5, rely=0.55, anchor="center")
    tarjeta.columnconfigure(0, weight=1)

    tk.Label(tarjeta, text="Acceso funcionario", font=("Segoe UI", 20),
             bg=COLOR_TARJETA, fg=COLOR_TEXTO).grid(row=0, column=0,
                                                    pady=(0, 6))
    tk.Frame(tarjeta, bg=COLOR_VERDE, height=3, width=60).grid(row=1, column=0,
                                                              pady=(0, 10))

    IngresoNombre = _campo(tarjeta, 2, "RUT Funcionario")
    IngresoClave = _campo(tarjeta, 4, "Clave Funcionario", show="•")

    # botón, llamamos al archivo estilo_boton
    boton_ingresar = estilo_boton.crear_boton_verde(
        tarjeta, "Ingresar", lambda: F.ventana_a(ventana))
    boton_ingresar.grid(row=6, column=0, sticky="ew", pady=(30, 0))

    IngresoNombre.focus_set()
    ventana.mainloop()