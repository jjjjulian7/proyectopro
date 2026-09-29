import tkinter as tk 
from tkinter import messagebox
from . import FuncionBotones as F

def abrir_carrito(event=None):
    # Validacion de datos (Fecha vencimiento, numero de tarjeta y cvv)
    def validar_datos(): 
        tarjeta = nroTarjeta.get() 
        cvv = IngresoCvv.get() 
        mes = FechaIngresoMes.get()
        anio = FechaIngresoAno.get()

        if not (len(tarjeta) == 16 and tarjeta.startswith("4345") and tarjeta.isdigit()): 
            messagebox.showerror("Error", "La tarjeta debe tener 16 dígitos y comenzar con 4345.") 
            return

        if not (len(cvv) == 3 and cvv.isdigit()): 
            messagebox.showerror("Error", "El código CVV debe tener exactamente 3 dígitos numéricos.") 
            return

        if not (mes.isdigit() and anio.isdigit()):
            messagebox.showerror("Error", "La fecha ingresada debe contener números válidos.")
            return

        if int(anio) < 26 or (int(anio) == 26 and int(mes) <= 10):
            messagebox.showerror("Error", "La fecha ingresada está vencida.")
            return  # <-- CORREGIDO: Evita que continue si la fecha está vencida

        messagebox.showinfo("Éxito", "Datos correctos. ¡Compra realizada con éxito!") 
        F.carrito.clear()
        ventana.destroy()

    # Callback para refrescar la ventana al eliminar o vaciar
    def refrescar_interfaz():
        ventana.destroy()
        abrir_carrito()

    ventana = tk.Tk() 
    ventana.title("Carrito") 
    ventana.geometry("700x600") 
    ventana.resizable(False, False) 

tabla = tk.Frame(ventana, bg="white")
    tabla.pack(fill="x", padx=20)
    tabla.columnconfigure(0, minsize=200)  # Producto
    tabla.columnconfigure(1, minsize=90)   # Precio
    tabla.columnconfigure(2, minsize=190)  # Cantidad
    tabla.columnconfigure(3, minsize=110)  # Sub total
    tabla.columnconfigure(4, weight=1)     # Botón eliminar

    pie = tk.Frame(ventana, bg="white")
    pie.pack(fill="x", padx=20, pady=(8, 0))

    lbl_total = tk.Label(pie, text="", font=FUENTE_NEGRITA, bg="white")

    def obtener_cantidad(item):
        try:
            return max(1, int(item["cantidad"].get()))
        except (tk.TclError, ValueError):
            return 1

    def actualizar():
        total = 0
        for item, lbl in zip(items, subtotales):
            sub = item["precio"] * obtener_cantidad(item)
            lbl.config(text=f"${sub} USD")
            total += sub
        lbl_total.config(text=f"Total ${total} USD")

    def eliminar(idx):
        del items[idx]
        dibujar_tabla()

    def continuar():
        ventana.destroy()  # vuelve a la página anterior

    def pagar():
        total = sum(i["precio"] * obtener_cantidad(i) for i in items)
        messagebox.showinfo("Pagos", f"Total a pagar: ${total} USD", parent=ventana)

    def linea(fila):
            tk.Frame(tabla, bg=COLOR_BORDE, height=1).grid(
                row=fila, column=0, columnspan=5, sticky="ew"
            )
             
    def dibujar_tabla():
        for w in tabla.winfo_children():
            w.destroy()
        subtotales.clear()

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
        
        dibujar_tabla()
        return ventana
        

        if __name__ == "__main__":
            root = tk.Tk()
            root.geometry("300x150")
            tk.Button(root, text="Ver carrito", command=lambda: abrir_carrito(root)).pack(expand=True)
            root.mainloop()
        
    # Si el carrito está vacío
    if not F.carrito.items:
        tk.Label(frame_lista_carrito, text="El carrito está vacío", bg="#d9d9d9").pack(anchor="w", pady=5)
    else:
        # Recorremos los ítems guardados en el objeto Carrito
        for item in F.carrito.items:
            subtotal_item = item["precio"] * item["cantidad"]
            texto = f"{item['nombre']} x{item['cantidad']} - ${subtotal_item:,.0f}"

            # Contenedor para cada fila de producto
            row_frame = tk.Frame(frame_lista_carrito, bg="#d9d9d9")
            row_frame.pack(fill="x", pady=2)

            tk.Label(row_frame, text=texto, bg="#d9d9d9", anchor="w").pack(side="left")

            # Etiqueta ELIMINAR con empaquetador .pack()
            eliminar = tk.Label(row_frame, text="[ELIMINAR]", bg="#d9d9d9", fg="red", cursor="hand2")
            eliminar.pack(side="right")
            
            # Al eliminar se ejecuta la función y luego se destruye/reabre la ventana
            eliminar.bind("<Button-1>", lambda event, i=item: [F.eliminar_producto(ventana, i), refrescar_interfaz()])

        subtotal, iva, total = F.mostrar_info()

        # Resumen de totales
        tk.Label(frame_lista_carrito, text=f"Subtotal: ${subtotal}", bg="#d9d9d9", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
        tk.Label(frame_lista_carrito, text=f"IVA (19%): ${iva}", bg="#d9d9d9", font=("Arial", 10, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Label(frame_lista_carrito, text=f"Total: ${total}", bg="#d9d9d9", font=("Arial", 11, "bold"), fg="#1b5e20").pack(anchor="w", pady=(2, 0))

    ventana.mainloop()