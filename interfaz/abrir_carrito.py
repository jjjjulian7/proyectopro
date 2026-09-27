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

    # Posicionamiento de los frames principales
    parte_izquierda = tk.Frame(ventana, bg="#f0f0f0") 
    parte_izquierda.place(x=0, y=0, width=250, height=600) 

    linea = tk.Frame(ventana, bg="black") 
    linea.place(x=250, y=0, width=2, height=600) 

    parte_derecha = tk.Frame(ventana, bg="#d9d9d9") 
    parte_derecha.place(x=252, y=0, width=448, height=600) 

    # CORREGIDO: Ancho ajustado a 230px para encajar en la parte izquierda (250px)
    frame_lista_carrito = tk.Frame(parte_izquierda, bg="#d9d9d9")
    frame_lista_carrito.place(x=10, y=10, width=230, height=580)

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

    # Parte derecha: Formulario de tarjeta
    lbl_tarjeta = tk.Label(parte_derecha, text="Número Tarjeta", bg="#d9d9d9") 
    lbl_tarjeta.grid(row=0, column=0, padx=(20, 10), pady=(210, 10), sticky="e") 

    nroTarjeta = tk.Entry(parte_derecha) 
    nroTarjeta.grid(row=0, column=1, columnspan=3, pady=(210, 10), sticky="w") 

    lbl_fecha = tk.Label(parte_derecha, text="Fecha Vencimiento", bg="#d9d9d9") 
    lbl_fecha.grid(row=1, column=0, padx=(20, 10), pady=(0, 10), sticky="e") 

    FechaIngresoMes = tk.Entry(parte_derecha, width=4) 
    FechaIngresoMes.grid(row=1, column=1, padx=(0, 2), pady=(0, 10), sticky="w") 

    lbl_separador = tk.Label(parte_derecha, text="/", bg="#d9d9d9") 
    lbl_separador.grid(row=1, column=2, padx=(0, 2), pady=(0, 10), sticky="w")  

    FechaIngresoAno = tk.Entry(parte_derecha, width=4) 
    FechaIngresoAno.grid(row=1, column=3, padx=(0, 0), pady=(0, 10), sticky="w") 

    lbl_cvv = tk.Label(parte_derecha, text="CVV", bg="#d9d9d9") 
    lbl_cvv.grid(row=2, column=0, padx=(20, 10), pady=(0, 10), sticky="e") 

    IngresoCvv = tk.Entry(parte_derecha, width=4) 
    IngresoCvv.grid(row=2, column=1, sticky="w") 

    btn_validar = tk.Button(parte_derecha, text="Comprar", command=validar_datos) 
    btn_validar.grid(row=3, column=0, columnspan=4, pady=(20, 0)) 

    boton_vaciar = tk.Button(parte_derecha, text="Vaciar carrito", command=lambda: [F.vaciarcarrito(ventana), refrescar_interfaz()])
    boton_vaciar.grid(row=4, column=0, columnspan=4, pady=(10, 0))

    ventana.mainloop()