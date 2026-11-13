import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from types import SimpleNamespace

from . import Client_ProyProgV2 as ClienteRed
from datos import bd_cupones
from datos import bd_envios
from clases.envio import Despacho

from .validar_tarjeta import abrir_validar_tarjeta

# Colores que ocupamos en la interfaz
COLOR_BORDE = "#dddddd"
COLOR_ROJO = "#d9534f"
COLOR_NARANJA = "#eeac57"
COLOR_VERDE = "#5cb85c"
FUENTE = ("Segoe UI", 10)
FUENTE_NEGRITA = ("Segoe UI", 10, "bold")

def abrir_carrito(carrito, event=None):
    """Abre la ventana del carrito (700x780).

    carrito: la instancia de clases.carrito.Carrito que ya usa tu página
             (la misma donde agregas los productos).
    """

    # Si ya existe una ventana principal, el carrito se abre encima ;
    # si no, crea la suya propia.
    root = tk._default_root
    if root is None:
        ventana = tk.Tk()
        ventana_propia = True
    else:
        ventana = tk.Toplevel(root)
        ventana_propia = False

    ventana.title("Carrito")
    ventana.geometry("700x780")
    ventana.resizable(False, False)
    ventana.configure(bg="white")
    ventana.timer = None # para que el carrito pueda cancelar el timer si se cierra la ventana
    segundos_restantes = 120  
    ventana.tiempo_restante = segundos_restantes
    def expirar_carrito():
        if ventana.timer is not None:
            ventana.after_cancel(ventana.timer)
            ventana.timer = None
        carrito.funcion_dibujar_tabla = None
        if carrito.items:
            messagebox.showinfo("Tiempo Agotado", "El carrito ha expirado por inactividad.", parent=ventana)
            carrito.vaciar_carrito()
        ventana.destroy()
    def descontar_tiempo():
        minutos = ventana.tiempo_restante // 60
        segundos =  ventana.tiempo_restante % 60
        lbl_timer.config(text=f"Tiempo restante: {minutos:02d}:{segundos:02d}")
        if ventana.tiempo_restante <= 0:
            expirar_carrito()
        else:
            ventana.tiempo_restante -= 1
            ventana.timer = ventana.after(1000, descontar_tiempo)
    
    def iniciar_resetear_timer(event=None):
        ventana.tiempo_restante = segundos_restantes
        if ventana.timer is not None:
            ventana.after_cancel(ventana.timer)
        descontar_tiempo() # 2 minutos
        
    ventana.bind("<Any-Button>", iniciar_resetear_timer)
    ventana.bind("<Key>", iniciar_resetear_timer)

    tk.Label(
        ventana, text="Carrito de compras", font=("Segoe UI", 22),
        bg="white", fg="#222222", anchor="w"
    ).pack(fill="x", padx=20, pady=(25, 10))
    lbl_timer = tk.Label(
        ventana, text="", font=("Segoe UI", 11, "bold"),
        bg="white", fg=COLOR_ROJO, anchor="e"
    )
    lbl_timer.pack(fill="x", padx=20)

    tabla = tk.Frame(ventana, bg="white")
    tabla.pack(fill="x", padx=20)
    tabla.columnconfigure(0, minsize=200)  # Producto
    tabla.columnconfigure(1, minsize=90)   # Precio
    tabla.columnconfigure(2, minsize=190)  # Cantidad
    tabla.columnconfigure(3, minsize=110)  # Sub total
    tabla.columnconfigure(4, weight=1)     # Botón eliminar

    # resumen de compra (subtotal + IVA + descuento)
    resumen = tk.Frame(ventana, bg="white")
    resumen.pack(fill="x", padx=20, pady=(10, 0))
    lbl_subtotal = tk.Label(resumen, text="", font=FUENTE, bg="white", anchor="e")
    lbl_subtotal.pack(fill="x")
    lbl_envio = tk.Label(resumen, text="", font=FUENTE, bg="white", anchor="e")
    lbl_envio.pack(fill="x")
    lbl_iva = tk.Label(resumen, text="", font=FUENTE, bg="white", anchor="e")
    lbl_iva.pack(fill="x")
    lbl_descuento = tk.Label(resumen, text="", font=FUENTE_NEGRITA, bg="white", fg="#1b5e20", anchor="e")
    lbl_descuento.pack(fill="x")

    ent_cupon = tk.Entry(resumen, font=FUENTE, bg="white", relief="solid", bd=1)
    ent_cupon.pack(side="left", pady=10, padx=(0, 5))

    def aplicar_cupon():
        codigo = ent_cupon.get().strip().upper()
        ok, resultado = bd_cupones.buscar_cupon(codigo)
        if ok:
            carrito.codigo_cupon = resultado["codigo"]
            carrito.tipo_cupon = resultado["tipo"]
            if resultado["tipo"] == "porcentaje":
                carrito.cupon = resultado["valor"] / 100.0
            else:
                carrito.cupon = resultado["valor"]
            actualizar_totales()
            messagebox.showinfo("Cupón aplicado", f"Cupón {carrito.codigo_cupon} aplicado correctamente.", parent=ventana)
        elif codigo == "DESCUENTO10":
            carrito.codigo_cupon = "DESCUENTO10"
            carrito.tipo_cupon = "porcentaje"
            carrito.cupon = 0.10
            actualizar_totales()
            messagebox.showinfo("Cupón aplicado", "Se ha aplicado un 10% de descuento adicional.", parent=ventana)
        else:
            messagebox.showwarning("Cupón inválido", resultado, parent=ventana)

    tk.Button(resumen, text="Aplicar cupón", command=aplicar_cupon, font=FUENTE, bg=COLOR_NARANJA, fg="white", activebackground="#d99a45", activeforeground="white", relief="flat", bd=0, padx=10, pady=5, cursor="hand2").pack(side="left", pady=10)

    # entrega: retiro en tienda o despacho a domicilio
    entrega = tk.LabelFrame(ventana, text=" Entrega ", font=FUENTE_NEGRITA, bg="white", bd=1, relief="solid")
    entrega.pack(fill="x", padx=20, pady=(8, 0))

    modalidad = tk.StringVar(value=Despacho.RETIRO)
    fila_modalidad = tk.Frame(entrega, bg="white")
    fila_modalidad.pack(fill="x", padx=8, pady=(4, 0))
    tk.Radiobutton(fila_modalidad, text=Despacho.RETIRO + " (sin costo)", variable=modalidad,
                   value=Despacho.RETIRO, font=FUENTE, bg="white", activebackground="white",
                   command=lambda: cambiar_modalidad()).pack(side="left")
    tk.Radiobutton(fila_modalidad, text=Despacho.DOMICILIO, variable=modalidad,
                   value=Despacho.DOMICILIO, font=FUENTE, bg="white", activebackground="white",
                   command=lambda: cambiar_modalidad()).pack(side="left", padx=(15, 0))

    # este formulario solo se muestra cuando elige despacho a domicilio
    form_envio = tk.Frame(entrega, bg="white")
    form_envio.columnconfigure(1, weight=1)
    form_envio.columnconfigure(3, weight=1)

    def campo_envio(texto, fila, columna):
        tk.Label(form_envio, text=texto, font=FUENTE, bg="white", anchor="w").grid(
            row=fila, column=columna, sticky="w", padx=(0, 5), pady=3)
        entrada = tk.Entry(form_envio, font=FUENTE, bg="white", relief="solid", bd=1)
        entrada.grid(row=fila, column=columna + 1, sticky="ew", padx=(0, 12), pady=3)
        return entrada

    ent_destinatario = campo_envio("Recibe", 0, 0)
    ent_direccion = campo_envio("Dirección", 0, 2)
    ent_comuna = campo_envio("Comuna", 1, 0)
    tk.Label(form_envio, text="Región", font=FUENTE, bg="white", anchor="w").grid(
        row=1, column=2, sticky="w", padx=(0, 5), pady=3)
    try:
        regiones = bd_envios.regiones_con_tarifa()
    except Exception:
        regiones = []
    cmb_region = ttk.Combobox(form_envio, state="readonly", font=FUENTE, values=regiones)
    cmb_region.grid(row=1, column=3, sticky="ew", padx=(0, 12), pady=3)

    lbl_fecha_entrega = tk.Label(entrega, text="", font=FUENTE, bg="white", fg="#1b5e20", anchor="w")
    lbl_fecha_entrega.pack(fill="x", padx=8, pady=(0, 4))

    pie = tk.Frame(ventana, bg="white")
    pie.pack(fill="x", padx=20, pady=(8, 0))

    lbl_total = tk.Label(pie, text="", font=FUENTE_NEGRITA, bg="white", fg="#1b5e20")
    lbl_total.pack(side="right", padx=(0, 10))

    # logica de la interfaz
    def fmt(valor):
        try:
            return f"{valor:,.0f}"
        except (TypeError, ValueError):
            return str(valor)

    def actualizar_totales():
        lbl_subtotal.config(text=f"Subtotal: ${fmt(carrito.calcular_subtotal())} CLP")
        if carrito.despacho.es_retiro() and modalidad.get() == Despacho.DOMICILIO:
            lbl_envio.config(text="Envío: elige una región para calcularlo")   # eligio domicilio pero falta la region
        elif carrito.despacho.es_retiro():
            lbl_envio.config(text="Envío (retiro en tienda): $0 CLP")
        elif carrito.calcular_envio() == 0 and carrito.items:
            lbl_envio.config(text="Envío: $0 CLP (envío gratis)")
        else:
            lbl_envio.config(text=f"Envío: ${fmt(carrito.calcular_envio())} CLP")
        fecha = carrito.despacho.fecha_estimada()
        lbl_fecha_entrega.config(
            text=f"Fecha estimada de entrega: {fecha.strftime('%d-%m-%Y')}" if fecha else "")
        lbl_iva.config(text=f"IVA (19%): ${fmt(carrito.calcular_iva())} CLP")
        lbl_total.config(text=f"Total ${fmt(carrito.calcular_total())} CLP")
        if carrito.cupon > 0:
            if carrito.tipo_cupon == "monto_fijo":
                lbl_descuento.config(text=f"Descuento activo: -${fmt(carrito.cupon)} CLP con cupón")
            else:
                lbl_descuento.config(text=f"Descuento activo: {int(carrito.cupon * 100)}% con cupón")
        else:
            lbl_descuento.config(text="")

    # muestra u oculta el formulario segun la modalidad y avisa al carrito
    def cambiar_modalidad():
        if modalidad.get() == Despacho.RETIRO:
            form_envio.pack_forget()
            carrito.elegir_retiro()
        else:
            form_envio.pack(fill="x", padx=8, pady=(4, 0), before=lbl_fecha_entrega)
            aplicar_despacho(silencioso=True)
        actualizar_totales()

    # valida los datos de despacho con el carrito y devuelve True si quedaron bien
    def aplicar_despacho(silencioso=False):
        ok, motivo = carrito.elegir_despacho(ent_destinatario.get(), ent_direccion.get(),
                                             ent_comuna.get(), cmb_region.get())
        if not ok and not silencioso:
            messagebox.showwarning("Datos de despacho", motivo, parent=ventana)
        return ok

    # al elegir la region ya se muestra el envio y la fecha aunque falten otros campos
    def al_cambiar_region(event=None):
        carrito.previsualizar_despacho(cmb_region.get())
        actualizar_totales()

    cmb_region.bind("<<ComboboxSelected>>", al_cambiar_region)

    def restar(item):
        # Baja de a 1; el minimo es 1 (para quitar todo esta el boton X).
        # No se redibuja aqui: cuando el servidor responde, carrito llama a dibujar_tabla.
        if item["cantidad"] <= 1:
            return
        carrito.eliminar_producto(item["id"], 1)

    def sumar(item):
        # Pide reservar 1 mas. Si no hay stock, el servidor responde ok=False
        # y carrito muestra el aviso. Solo se necesitan id y nombre del producto.
        producto = SimpleNamespace(id=item["id"], nombre=item["nombre"])
        carrito.agregar_producto(producto, 1, carrito.usuario)

    def eliminar(item):
        id_producto = item["id"]
        cantidad = item["cantidad"]
        # Quita el producto completo y restaura su stock
        carrito.eliminar_producto(id_producto, cantidad)  # Llama al método para vaciar el carrito y restaurar el stock
        refrescar_interfaz()

    # refrescar la ventana al eliminar o vaciar
    def refrescar_interfaz():
        dibujar_tabla()

    def continuar():
        if ventana.timer is not None:
            ventana.after_cancel(ventana.timer)
            ventana.timer = None
        carrito.funcion_dibujar_tabla = None
        ventana.destroy()

    def pagar():
        print("click en pagar")  # temporal: borrar cuando todo funcione
        if not carrito.items:
            messagebox.showwarning("Pagos", "El carrito está vacío.", parent=ventana)
            return
        # si eligio despacho a domicilio no deja pagar hasta que los datos esten completos
        if modalidad.get() == Despacho.DOMICILIO and not aplicar_despacho():
            return
        actualizar_totales()
        from . import FuncionBotones as F  # import aqui adentro para evitar import circular
        cliente = F.usuario_actual or "Invitado"
        abrir_validar_tarjeta(ventana, carrito.calcular_total(), carrito, cliente)

    def linea(fila):
        tk.Frame(tabla, bg=COLOR_BORDE, height=1).grid(
            row=fila, column=0, columnspan=5, sticky="ew"
        )

    def dibujar_tabla():
        for w in tabla.winfo_children():
            w.destroy()

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

            # Cantidad: boton -, numero fijo (no editable) y boton +
            frame_cant = tk.Frame(tabla, bg="white")
            frame_cant.grid(row=fila, column=2, sticky="w", padx=(4, 0))

            tk.Button(
                frame_cant, text="-", font=FUENTE_NEGRITA, width=2,
                bg=COLOR_NARANJA, fg="white", activebackground="#d99a45",
                activeforeground="white", relief="flat", bd=0, cursor="hand2",
                command=lambda it=item: restar(it)
            ).pack(side="left")

            tk.Label(
                frame_cant, text=str(item["cantidad"]), font=FUENTE_NEGRITA,
                bg="white", width=4
            ).pack(side="left", padx=4)

            tk.Button(
                frame_cant, text="+", font=FUENTE_NEGRITA, width=2,
                bg=COLOR_VERDE, fg="white", activebackground="#4cae4c",
                activeforeground="white", relief="flat", bd=0, cursor="hand2",
                command=lambda it=item: sumar(it)
            ).pack(side="left")

            tk.Label(
                tabla, text=f"${fmt(item['precio'] * item['cantidad'])} CLP",
                font=FUENTE, bg="white", anchor="w"
            ).grid(row=fila, column=3, sticky="w", padx=(4, 0))

            tk.Button(
                tabla, text="X", font=("Segoe UI Emoji", 10),
                bg=COLOR_ROJO, fg="white", activebackground="#c9302c",
                activeforeground="white", relief="flat", bd=0,
                width=5, pady=3, cursor="hand2",
                command=lambda it=item: eliminar(it)
            ).grid(row=fila, column=4, sticky="w")

            linea(fila + 1)

        actualizar_totales()

    # botones , se pueden mover a FuncionBotones quizas mas adelante
    tk.Button(
        pie, text="<  Continue Comprando", font=FUENTE,
        bg=COLOR_NARANJA, fg="white", activebackground="#d99a45",
        activeforeground="white", relief="flat", bd=0,
        padx=12, pady=5, cursor="hand2", command=continuar
    ).pack(side="left")

    tk.Button(
        pie, text="Pagos  >", font=FUENTE,
        bg=COLOR_VERDE, fg="white", activebackground="#4cae4c",
        activeforeground="white", relief="flat", bd=0,
        width=12, pady=5, cursor="hand2", command=pagar
    ).pack(side="right")


    def vaciar():
        if not carrito.items:
            return
        carrito.vaciar_carrito()  # el servidor restaura el stock y luego redibuja la tabla
 
    tk.Button(
        ventana, text="Vaciar carrito", font=FUENTE,
        bg=COLOR_ROJO, fg="white", activebackground="#c9302c",
        activeforeground="white", relief="flat", bd=0,
        padx=12, pady=5, cursor="hand2", command=vaciar
    ).pack(pady=(20, 0))
 
    # Cierre limpio de la ventana cancelando cualquier timer activo
    def cerrar_carrito():
        if ventana.timer is not None:
            ventana.after_cancel(ventana.timer)
            ventana.timer = None
        carrito.funcion_dibujar_tabla = None
        ventana.destroy()

    ventana.protocol("WM_DELETE_WINDOW", cerrar_carrito)

    def al_destruir(event):
        if event.widget is ventana:
            carrito.funcion_dibujar_tabla = None
            if ventana.timer is not None:
                ventana.after_cancel(ventana.timer)
                ventana.timer = None
    ventana.bind("<Destroy>", al_destruir)
    
    iniciar_resetear_timer()  # inicia el timer de expiración del carrito
 
    carrito.funcion_dibujar_tabla = dibujar_tabla  # para que el carrito pueda actualizar la interfaz
    carrito.elegir_retiro()  # la ventana siempre parte con retiro en tienda
    dibujar_tabla()
 
    ClienteRed.conectar_interfaz_vaciar(carrito.procesar_respuesta_vaciar)
    ClienteRed.conectar_interfaz_reponer(carrito.procesar_respuesta_eliminar)
    ClienteRed.conectar_interfaz_reserva(carrito.procesar_respuesta_reservar)
 
    if ventana_propia:
        ventana.mainloop()
    return ventana
