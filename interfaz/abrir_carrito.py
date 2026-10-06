import tkinter as tk
from tkinter import messagebox

from proyectopro.clases.Venta import venta
from .validar_tarjeta import abrir_validar_tarjeta

# Colores que ocupamos en la interfaz
COLOR_BORDE = "#dddddd"
COLOR_ROJO = "#d9534f"
COLOR_NARANJA = "#eeac57"
COLOR_VERDE = "#5cb85c"
FUENTE = ("Segoe UI", 10)
FUENTE_NEGRITA = ("Segoe UI", 10, "bold")


def abrir_carrito(carrito, event=None):
    """Abre la ventana del carrito (700x600).

    carrito: la instancia de clases.carrito.Carrito que ya usa tu página
             (la misma donde agregas los productos).
    """

    # Si ya existe una ventana principal, el carrito se abre encima (Toplevel);
    # si no, crea la suya propia.
    root = tk._default_root
    if root is None:
        ventana = tk.Tk()
        ventana_propia = True
    else:
        ventana = tk.Toplevel(root)
        ventana_propia = False

    ventana.title("Carrito")
    ventana.geometry("700x600")
    ventana.resizable(False, False)
    ventana.configure(bg="white")

    subtotales = []   # labels de sub total de cada fila
    variables = []    # IntVar de cada spinbox (evita que se pierdan)

    tk.Label(
        ventana, text="Carrito de compras", font=("Segoe UI", 22),
        bg="white", fg="#222222", anchor="w"
    ).pack(fill="x", padx=20, pady=(25, 10))

    tabla = tk.Frame(ventana, bg="white")
    tabla.pack(fill="x", padx=20)
    tabla.columnconfigure(0, minsize=200)  # Producto
    tabla.columnconfigure(1, minsize=90)   # Precio
    tabla.columnconfigure(2, minsize=190)  # Cantidad
    tabla.columnconfigure(3, minsize=110)  # Sub total
    tabla.columnconfigure(4, weight=1)     # Botón eliminar

    # resumen de compra (subtotal + IVA)
    resumen = tk.Frame(ventana, bg="white")
    resumen.pack(fill="x", padx=20, pady=(10, 0))
    lbl_subtotal = tk.Label(resumen, text="", font=FUENTE, bg="white", anchor="e")
    lbl_subtotal.pack(fill="x")
    lbl_iva = tk.Label(resumen, text="", font=FUENTE, bg="white", anchor="e")
    lbl_iva.pack(fill="x")

    pie = tk.Frame(ventana, bg="white")
    pie.pack(fill="x", padx=20, pady=(8, 0))

    lbl_total = tk.Label(pie, text="", font=FUENTE_NEGRITA, bg="white", fg="#1b5e20")

    # logica de la interfaz
    def fmt(valor):
        try:
            return f"{valor:,.0f}"
        except (TypeError, ValueError):
            return str(valor)

    def actualizar_totales():
        lbl_subtotal.config(text=f"Subtotal: ${fmt(carrito.calcular_subtotal())} CLP")
        lbl_iva.config(text=f"IVA (19%): ${fmt(carrito.calcular_iva())} CLP")
        lbl_total.config(text=f"Total ${fmt(carrito.calcular_total())} CLP")

    def cambiar_cantidad(item, var, spin, lbl_sub):
        # Por ahora solo se puede BAJAR la cantidad (el stock se restaura en la bd)
        try:
            nueva = int(var.get())
        except (tk.TclError, ValueError):
            nueva = item["cantidad"]
        nueva = max(1, min(nueva, item["cantidad"]))
        diferencia = item["cantidad"] - nueva
        if diferencia > 0:
            carrito.eliminar_producto(item, diferencia)
        var.set(nueva)
        spin.config(to=nueva)
        lbl_sub.config(text=f"${fmt(item['precio'] * item['cantidad'])} CLP")
        actualizar_totales()

    def eliminar(item):
        # Quita el producto completo y restaura su stock
        carrito.eliminar_producto(item, item["cantidad"])
        refrescar_interfaz()

    #refrescar la ventana al eliminar o vaciar
    def refrescar_interfaz():
        dibujar_tabla()

    def continuar():
        ventana.destroy()  # vuelve a la página anterior

    def pagar():
        print("click en pagar")  # temporal: borrar cuando todo funcione
        if not carrito.items:
            messagebox.showwarning("Pagos", "El carrito está vacío.", parent=ventana)
            return
        abrir_validar_tarjeta(ventana, carrito.calcular_total(), carrito)

    def linea(fila):
        tk.Frame(tabla, bg=COLOR_BORDE, height=1).grid(
            row=fila, column=0, columnspan=5, sticky="ew"
        )

    def dibujar_tabla():
        for w in tabla.winfo_children():
            w.destroy()
        subtotales.clear()
        variables.clear()

        # Encabezados
        for col, texto in enumerate(["Producto", "Precio", "Cantidad", "Sub total"]):
            tk.Label(tabla, text=texto, font=FUENTE_NEGRITA, bg="white",
                     anchor="w").grid(row=0, column=col, sticky="w", pady=8, padx=(4, 0))
        linea(1)

        # Si el carrito está vacío
        if not carrito.items:
            tk.Label(tabla, text="El carrito está vacío", font=FUENTE,
                     bg="white", fg="#777777").grid(
                row=2, column=0, columnspan=5, sticky="w", pady=15, padx=(4, 0))
            actualizar_totales()
            return

        # Recorremos los ítems guardados en el objeto Carrito
        for i, item in enumerate(carrito.items):
            fila = 2 + i * 2

            tk.Label(tabla, text=item["nombre"], font=FUENTE, bg="white",
                     anchor="w").grid(row=fila, column=0, sticky="w", pady=10, padx=(4, 0))
            tk.Label(tabla, text=f"${fmt(item['precio'])} CLP", font=FUENTE, bg="white",
                     anchor="w").grid(row=fila, column=1, sticky="w", padx=(4, 0))

            lbl_sub = tk.Label(
                tabla, text=f"${fmt(item['precio'] * item['cantidad'])} CLP",
                font=FUENTE, bg="white", anchor="w")
            lbl_sub.grid(row=fila, column=3, sticky="w", padx=(4, 0))
            subtotales.append(lbl_sub)

            var = tk.IntVar(master=ventana, value=item["cantidad"])
            variables.append(var)
            spin = tk.Spinbox(
                tabla, from_=1, to=item["cantidad"], width=4, font=FUENTE,
                textvariable=var, relief="solid", bd=1
            )
            spin.config(command=lambda it=item, v=var, s=spin, l=lbl_sub:
                        cambiar_cantidad(it, v, s, l))
            spin.grid(row=fila, column=2, sticky="w", padx=(4, 0))
            for evento in ("<Return>", "<FocusOut>"):
                spin.bind(evento, lambda e, it=item, v=var, s=spin, l=lbl_sub:
                          cambiar_cantidad(it, v, s, l))

            tk.Button(
                tabla, text="🗑", font=("Segoe UI Emoji", 10),
                bg=COLOR_ROJO, fg="white", activebackground="#c9302c",
                activeforeground="white", relief="flat", bd=0,
                width=5, pady=3, cursor="hand2",
                command=lambda it=item: eliminar(it)
            ).grid(row=fila, column=4, sticky="w")

            linea(fila + 1)

        actualizar_totales()

    # botones , se pueden mover a FuncionBotones quizas mas adelante
    tk.Button(
        pie, text="‹  Continue Comprando", font=FUENTE,
        bg=COLOR_NARANJA, fg="white", activebackground="#d99a45",
        activeforeground="white", relief="flat", bd=0,
        padx=12, pady=5, cursor="hand2", command=continuar
    ).pack(side="left")

    tk.Button(
        pie, text="Pagos  ›", font=FUENTE,
        bg=COLOR_VERDE, fg="white", activebackground="#4cae4c",
        activeforeground="white", relief="flat", bd=0,
        width=12, pady=5, cursor="hand2", command=pagar
    ).pack(side="right")

    lbl_total.pack(side="right", padx=30)
##Copiada de un commit anterior , falta por arreglar
    boton_vaciar=tk.Button(ventana,text="Vaciar carrito", command=lambda:F.vaciarcarrito(ventana))
    boton_vaciar.grid(row=4, column=0, columnspan=4, pady=(20, 0))
    ventana.mainloop()
    boton_vaciar = tk.Button(ventana, text="Vaciar carrito", command=lambda: [F.vaciarcarrito(ventana), refrescar_interfaz()])
    boton_vaciar.grid(row=4, column=0, columnspan=4, pady=(10, 0))

    dibujar_tabla()

    if ventana_propia:
        ventana.mainloop()
    return ventana