import tkinter as tk

FUENTE = ("Segoe UI", 10)


def abrir_validar_tarjeta(padre, total, carrito=None):
    print("validar_tarjeta abierta")  # temporal
    ventana = tk.Toplevel(padre)
    ventana.title("Validar tarjeta")
    ventana.geometry("400x350")
    ventana.resizable(False, False)
    ventana.configure(bg="white")

    ventana.transient(padre)
    ventana.wait_visibility()
    ventana.grab_set()
    ventana.focus_set()

    tk.Label(
        ventana, text=f"Total a pagar: ${total:,.0f} CLP",
        font=FUENTE, bg="white"
    ).pack(pady=20)

    # Aquí irán los campos y la validación

    return ventana