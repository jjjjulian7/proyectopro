import tkinter as tk 
from tkinter import messagebox
from . import FuncionBotones as F

def abrir_carrito():

    def validar_datos(): 
        tarjeta = nroTarjeta.get() 
        cvv = IngresoCvv.get() 
         
        if not (len(tarjeta) == 16 and tarjeta.startswith("4345") and tarjeta.isdigit()): 
            messagebox.showerror("Error", "La tarjeta debe tener 16 dígitos y comenzar con 4345.") 
            return

        if not (len(cvv) == 3 and cvv.isdigit()): 
            messagebox.showerror("Error", "El código CVV debe tener exactamente 3 dígitos numéricos.") 
            return
        mes = FechaIngresoMes.get()
        anio = FechaIngresoAno.get()
        if int(anio) < 26 or int(anio) == 26 and int(mes) <= 10:
            messagebox.showerror("Error", "La fecha ingresada está vencida.")

        messagebox.showinfo("Éxito", "Datos correctos. ¡Compra realizada con éxito!") 
        F.carrito.clear()
        ventana.destroy()
         
    ventana = tk.Tk() 
    ventana.title("Carrito") 
    ventana.geometry("700x600") 
    ventana.resizable(False, False) 

    parte_izquierda = tk.Frame(ventana, bg="#f0f0f0") 
    parte_izquierda.place(x=0, y=0, width=250, height=600) 

    linea = tk.Frame(ventana, bg="black") 
    linea.place(x=250, y=0, width=2, height=600) 

    parte_derecha = tk.Frame(ventana, bg="#d9d9d9") 
    parte_derecha.place(x=252, y=0, width=448, height=600) 

    frame_lista_carrito = tk.Frame(parte_izquierda, bg="#d9d9d9")
    frame_lista_carrito.place(x=10, y=10, width=428, height=190)

    if not F.carrito:
        tk.Label(frame_lista_carrito, text="El carrito está vacío", bg="#d9d9d9").pack(anchor="w", pady=5)
    else:
        for item in F.carrito:
            subtotal = item["precio"] * item["cantidad"]#se calcula
            texto = f"{item['nombre']} x{item['cantidad']} - $ {subtotal}"
            tk.Label(frame_lista_carrito, text=texto, bg="#d9d9d9", anchor="w").pack(fill="x", pady=2)

        total = F.calcular_total()
        tk.Label(frame_lista_carrito, text=f"Total: $ {total}", bg="#d9d9d9", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))

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

    ventana.mainloop()
