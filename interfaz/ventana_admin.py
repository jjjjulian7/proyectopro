import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
import sqlite3
from . import FuncionBotones as F
from datos import bd
from datos import bd_carrito
from datos import bd_ventas
from datos import bd_cupones
from datos import bd_envios
from datetime import datetime


def ejecutar():
    bd_cupones.crear_tabla()    # asegura que exista la tabla de cupones
    bd_envios.crear_tabla()     # asegura que existan las tarifas de envio

    ventana = tk.Tk()
    ventana.title("MaulencitosMarketADMIN")
    ventana.geometry("1280x720")

    #frames padres
    Frame_botones=tk.Frame(ventana)
    Frame_botones.config(bg="#f1f3f5")
    Frame_contenido=tk.Frame(ventana)
    Frame_botones.grid(row=0, column=0, columnspan=2, sticky="ew")
    Frame_contenido.grid(row=1, column=0, sticky="n", padx=20, pady=20)
    Frame_producto=tk.Frame(ventana)
    Frame_producto.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=20)

    ventana.grid_columnconfigure(0, minsize=400)    # Columna del panel izquierdo: ancho minimo fijo
    ventana.grid_columnconfigure(1, weight=1)       # columna de la tabla: se estira con la ventana
    ventana.grid_rowconfigure(1, weight=1)          # Fila del contenido tambien se estira

    Frame_botones.grid_columnconfigure(0, weight=0)
    Frame_botones.grid_columnconfigure(1, weight=0)
    Frame_botones.grid_columnconfigure(2, weight=0)
    Frame_botones.grid_columnconfigure(3, weight=0)
    Frame_botones.grid_columnconfigure(4, weight=0)
    Frame_botones.grid_columnconfigure(5, weight=0)
    Frame_botones.grid_columnconfigure(6, weight=0)
    Frame_botones.grid_columnconfigure(7, weight=0)
    Frame_botones.grid_columnconfigure(8, weight=1)
    Frame_botones.grid_columnconfigure(9, weight=0)

    #Frae hijos de Frame contenido
    Frame_ingreso=tk.Frame(Frame_contenido)
    Frame_estadisticas=tk.Frame(Frame_contenido)
    lista_F=[Frame_ingreso,Frame_estadisticas]#esto es para que le pasemos los frame a la funcion mostrar frame asi los va a poder ocultar y mostrar el contenido que elija el usuario

    #botones
    boton_ingreso=tk.Button(Frame_botones,text="Ingresar producto",command=lambda:mostrar_seccion(Frame_ingreso))
    boton_estadisticas=tk.Button(Frame_botones,text="Estadísticas",command=lambda:mostrar_seccion(Frame_estadisticas))
    boton_ingreso.grid(column=1,row=1, padx=(20,0))
    boton_estadisticas.grid(column=4,row=1)

    #boton para asignar permisos de admin
    frame_admin = tk.Frame(Frame_contenido)
    lista_F.append(frame_admin)

    #frame para ver los carritos de los usuarios
    frame_carritos = tk.Frame(Frame_contenido)
    lista_F.append(frame_carritos)

    frame_ventas = tk.Frame(Frame_contenido)
    lista_F.append(frame_ventas)
    frame_cupones = tk.Frame(Frame_contenido)
    lista_F.append(frame_cupones)
    frame_envios = tk.Frame(Frame_contenido)
    lista_F.append(frame_envios)

    def mostrar_seccion(frame):
        F.mostrar_frame(frame, lista_F)

    boton_admin = tk.Button(Frame_botones, text="Hacer admin", command=lambda: mostrar_seccion(frame_admin))
    boton_admin.grid(row=1, column=5, padx=(20, 0), pady=10, sticky="w")

    #frame_ingreso
    titulo_formulario =tk.Label(Frame_ingreso, text="Registrar Producto",
                                bg="#dcdde1", font=("Segoe UI", 12), pady=14)
    titulo_formulario.grid(row=0, column=1, sticky="ew")
    tk.Label(Frame_ingreso,text="Nombre del producto").grid(row=1,column=1, sticky="w")
    tk.Label(Frame_ingreso,text="Precio").grid(row=3,column=1, sticky="w")
    tk.Label(Frame_ingreso,text="Stock").grid(row=5,column=1, sticky="w")
    tk.Label(Frame_ingreso,text="Categoria").grid(row=7,column=1, sticky="w")

    nombre=tk.Entry(Frame_ingreso, width=30,
                    highlightthickness=1,               # Agregamos grosor al borde del boton
                    highlightbackground="#ced4da",    # Color del borde
                    highlightcolor="#0d6efd")         #Color del borde al hacer clic
    precio=tk.Entry(Frame_ingreso, width=30, highlightthickness=1,highlightbackground="#ced4da", highlightcolor="#0d6efd") 
    stock=tk.Entry(Frame_ingreso, width=30, highlightthickness=1,highlightbackground="#ced4da", highlightcolor="#0d6efd") 
    categoria=tk.Entry(Frame_ingreso, width=30, highlightthickness=1,highlightbackground="#ced4da", highlightcolor="#0d6efd") 

    nombre.grid(row=2,column=1, ipady=6)                # ipady = mas alto por dentro
    precio.grid(row=4,column=1, ipady=6)
    stock.grid(row=6,column=1, ipady=6)
    categoria.grid(row=8,column=1, ipady=6)

    id_editando = None # Producto que se esta editando

    def limpiar_formulario():
        nonlocal id_editando        # Con nonlocal editamos la variable desde afura de la funcion
        id_editando = None          # Volvemos al modo registrar producto
        for campo in (nombre, precio, stock, categoria):
            campo.delete(0, tk.END)     # Vaciamos los entry que se hayan asigando antes
        boton.grid_configure(sticky="")
        boton.config(text="Ingresar")   # Devolvemos el boton a su texto original
        boton_cancelar.grid_remove()    # Ocultamos el boton cancelar
        titulo_formulario.config(text="Registro de productos")

    def guardar():
        # Si se guarda el producto correctamente limpiamos el formulario
        # Sino, dejamos lo escrito para que sea correjido
        if F.guardar_producto(id_editando, nombre, precio, stock, categoria, Frame_producto):
            limpiar_formulario()

    def iniciar_edicion(id_producto):
        nonlocal id_editando
        producto = F.inventario.buscar_producto(1, id_producto) # buscamos por id
        if producto is None:
            return
        mostrar_seccion(Frame_ingreso)      # mostramos el formulario
        limpiar_formulario()                # vaciamos si ya habia algo
        id_editando = id_producto          

        for campo, valor in ((nombre, producto.nombre), (precio, producto.precio), (stock, producto.stock), (categoria, producto.categoria)):
            campo.insert(0, str(valor))     # los entry solo aceptan texto, asi que se transforman antes 

        titulo_formulario.config(text=f"Editando producto #{id_producto}")      # Cambiamos el titulo del formulario
        boton.grid_configure(sticky="w")        
        boton.config(text="Guardar")
        boton_cancelar.grid(row=9, column=1,  sticky="e",pady=(16,0))     # mostramos boton cancelar

    boton= tk.Button(Frame_ingreso, text="Ingresar", command=guardar, bg="#0d6efd", fg="white", relief="flat", bd=0, padx=14,pady=6)
    boton_cancelar= tk.Button(Frame_ingreso, text="Cancelar", command=limpiar_formulario, bg="#fd0d0d", fg="white", relief="flat",bd=0, padx=14,pady=6)
    boton.grid(row=9, column=1, pady=((16,0)))

    Frame_producto.al_editar = iniciar_edicion # DEjamos guardada la funcion dentro del Frame de la tabla


    # Frame para asignar permisos de administrador

    frame_admin.grid_columnconfigure(0, weight=1)    # la columna se estira al ancho del panel

    # Título gris, igual que el del formulario
    tk.Label(frame_admin, text="Hacer administrador",
             bg="#dcdde1", font=("Segoe UI", 12), pady=14).grid(row=0, column=0, sticky="ew", pady=(0, 10))


    tk.Label(frame_admin, text="Nombre del usuario", font=("Segoe UI", 10),
             anchor="w").grid(row=1, column=0, sticky="ew", pady=(8, 2))
    entrada_nombre_admin = tk.Entry(frame_admin, width=30, relief="flat",
                                    highlightthickness=1,
                                    highlightbackground="#ced4da",    # borde gris normal
                                    highlightcolor="#0d6efd")         # borde azul al hacer clic
    entrada_nombre_admin.grid(row=2, column=0, sticky="ew", ipady=6)

    tk.Label(frame_admin, text="RUT del administrador", font=("Segoe UI", 10),
             anchor="w").grid(row=3, column=0, sticky="ew", pady=(8, 2))
    entrada_rut_admin = tk.Entry(frame_admin, width=30, relief="flat", highlightthickness=1,highlightbackground="#ced4da", highlightcolor="#0d6efd")
    entrada_rut_admin.grid(row=4, column=0, sticky="ew", ipady=6)

    def hacer_admin():
        nombre = entrada_nombre_admin.get().strip()
        rut = entrada_rut_admin.get().strip()

        if not F.hacer_admin(nombre, rut):
            return

        entrada_nombre_admin.delete(0, tk.END)
        entrada_rut_admin.delete(0, tk.END)
        mostrar_seccion(Frame_ingreso)

    boton_hacer_admin = tk.Button(frame_admin, text="Hacer admin", command=hacer_admin,
                                  bg="#0d6efd", fg="white", activebackground="#0d6efd", activeforeground="white",
                                  relief="flat", bd=0, font=("Segoe UI", 10), padx=14, pady=6)
    boton_hacer_admin.grid(row=5, column=0, sticky="w", pady=(16, 0))

    # Frame para crear cupones
    frame_cupones.grid_columnconfigure(0, weight=1)

    tk.Label(frame_cupones, text="Crear cupones",
             bg="#dcdde1", font=("Segoe UI", 12), pady=14).grid(row=0, column=0, sticky="ew", pady=(0, 10))

    tk.Label(frame_cupones, text="Código del cupón", font=("Segoe UI", 10),
             anchor="w").grid(row=1, column=0, sticky="ew", pady=(8, 2))
    entrada_codigo_cupon = tk.Entry(frame_cupones, width=30, relief="flat",
                                    highlightthickness=1,
                                    highlightbackground="#ced4da",
                                    highlightcolor="#0d6efd")
    entrada_codigo_cupon.grid(row=2, column=0, sticky="ew", ipady=6)

    tk.Label(frame_cupones, text="Tipo de descuento", font=("Segoe UI", 10),
             anchor="w").grid(row=3, column=0, sticky="ew", pady=(8, 2))
    selector_tipo_cupon = ttk.Combobox(frame_cupones, state="readonly", font=("Segoe UI", 10),
                                       values=["Porcentaje (%)", "Monto fijo (CLP)"])
    selector_tipo_cupon.current(0)
    selector_tipo_cupon.grid(row=4, column=0, sticky="ew")

    tk.Label(frame_cupones, text="Valor del descuento", font=("Segoe UI", 10),
             anchor="w").grid(row=5, column=0, sticky="ew", pady=(8, 2))
    entrada_descuento_cupon = tk.Entry(frame_cupones, width=30, relief="flat",
                                       highlightthickness=1,
                                       highlightbackground="#ced4da",
                                       highlightcolor="#0d6efd")
    entrada_descuento_cupon.grid(row=6, column=0, sticky="ew", ipady=6)

    tk.Label(frame_cupones, text="Vencimiento (DD-MM-AAAA)", font=("Segoe UI", 10),
             anchor="w").grid(row=7, column=0, sticky="ew", pady=(8, 2))
    entrada_vence_cupon = tk.Entry(frame_cupones, width=30, relief="flat",
                                   highlightthickness=1,
                                   highlightbackground="#ced4da",
                                   highlightcolor="#0d6efd")
    entrada_vence_cupon.grid(row=8, column=0, sticky="ew", ipady=6)

    tk.Label(frame_cupones, text="Usos máximos", font=("Segoe UI", 10),
             anchor="w").grid(row=9, column=0, sticky="ew", pady=(8, 2))
    entrada_usos_cupon = tk.Entry(frame_cupones, width=30, relief="flat",
                                  highlightthickness=1,
                                  highlightbackground="#ced4da",
                                  highlightcolor="#0d6efd")
    entrada_usos_cupon.grid(row=10, column=0, sticky="ew", ipady=6)

    def crear_cupon_admin():
        codigo = entrada_codigo_cupon.get()
        if selector_tipo_cupon.current() == 0:
            tipo = "porcentaje"
        else:
            tipo = "monto_fijo"
        valor = entrada_descuento_cupon.get()
        fecha = entrada_vence_cupon.get()
        usos = entrada_usos_cupon.get()

        ok, mensaje = bd_cupones.crear_cupon(codigo, tipo, valor, fecha, usos)
        if ok:
            entrada_codigo_cupon.delete(0, tk.END)
            entrada_descuento_cupon.delete(0, tk.END)
            entrada_vence_cupon.delete(0, tk.END)
            entrada_usos_cupon.delete(0, tk.END)
            messagebox.showinfo("Cupón creado", mensaje, parent=ventana)
        else:
            messagebox.showwarning("Error", mensaje, parent=ventana)

    boton_guardar_cupon = tk.Button(frame_cupones, text="Crear cupón", command=crear_cupon_admin,
                                    bg="#0d6efd", fg="white", activebackground="#0d6efd", activeforeground="white",
                                    relief="flat", bd=0, font=("Segoe UI", 10), padx=14, pady=6)
    boton_guardar_cupon.grid(row=11, column=0, sticky="w", pady=(16, 0))


    # Frame de tarifas de envio el admin las define y el carrito del cliente las lee de la bd
    frame_envios.grid_columnconfigure(0, weight=1)
    frame_envios.grid_columnconfigure(1, weight=1)

    tk.Label(frame_envios, text="Tarifas de envío", bg="#dcdde1", font=("Segoe UI", 12),
             pady=14).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
    tk.Label(frame_envios, text="Haz click en una región para editar su tarifa", font=("Segoe UI", 10),
             anchor="w").grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))

    tabla_tarifas = ttk.Treeview(frame_envios, columns=("region", "costo", "dias"),
                                 show="headings", style="Productos.Treeview", height=8)
    for col, (texto, ancho, ancla) in {
        "region": ("REGIÓN", 170, "w"),
        "costo":  ("COSTO", 80, "e"),
        "dias":   ("DÍAS HÁB.", 70, "center"),
    }.items():
        tabla_tarifas.heading(col, text=texto)
        tabla_tarifas.column(col, width=ancho, anchor=ancla)
    tabla_tarifas.tag_configure("par", background="#ffffff")
    tabla_tarifas.tag_configure("impar", background="#e0e0e0")
    tabla_tarifas.grid(row=2, column=0, columnspan=2, sticky="ew")

    tk.Label(frame_envios, text="Costo de envío (CLP)", font=("Segoe UI", 10), anchor="w").grid(row=3, column=0, sticky="ew", pady=(10, 2))
    tk.Label(frame_envios, text="Días hábiles", font=("Segoe UI", 10), anchor="w").grid(row=3, column=1, sticky="ew", pady=(10, 2), padx=(10, 0))
    entrada_costo_envio = tk.Entry(frame_envios, width=12, relief="flat", highlightthickness=1,
                                   highlightbackground="#ced4da", highlightcolor="#0d6efd")
    entrada_costo_envio.grid(row=4, column=0, sticky="ew", ipady=6)
    entrada_dias_envio = tk.Entry(frame_envios, width=12, relief="flat", highlightthickness=1,
                                  highlightbackground="#ced4da", highlightcolor="#0d6efd")
    entrada_dias_envio.grid(row=4, column=1, sticky="ew", ipady=6, padx=(10, 0))

    etiqueta_region_envio = tk.Label(frame_envios, text="Región: (ninguna seleccionada)", font=("Segoe UI", 10), anchor="w")
    etiqueta_region_envio.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(6, 0))
    region_editando = {"nombre": None}  # diccionario para poder cambiarlo desde las funciones de abajo

    def refrescar_tarifas():
        tabla_tarifas.delete(*tabla_tarifas.get_children())
        try:
            for i, (region_t, costo_t, dias_t) in enumerate(bd_envios.listar_tarifas()):
                tabla_tarifas.insert("", "end", iid=region_t,
                                     values=(region_t, f"${costo_t:,.0f}", dias_t),
                                     tags=("par" if i % 2 == 0 else "impar",))
            monto_minimo, region_tienda = bd_envios.obtener_config()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudieron leer las tarifas: {e}", parent=ventana)
            return
        entrada_monto_gratis.delete(0, tk.END)
        entrada_monto_gratis.insert(0, str(int(monto_minimo)))
        selector_region_tienda.set(region_tienda)

    # al hacer click en una region se copian sus valores a los campos de edicion
    def al_elegir_tarifa(event=None):
        seleccion = tabla_tarifas.selection()
        if not seleccion:
            return
        region_t = seleccion[0]
        fila = bd_envios.obtener_tarifa(region_t)
        if fila is None:
            return
        region_editando["nombre"] = region_t
        etiqueta_region_envio.config(text=f"Región: {region_t}")
        entrada_costo_envio.delete(0, tk.END)
        entrada_costo_envio.insert(0, str(int(fila[1])))
        entrada_dias_envio.delete(0, tk.END)
        entrada_dias_envio.insert(0, str(fila[2]))

    tabla_tarifas.bind("<<TreeviewSelect>>", al_elegir_tarifa)

    def guardar_tarifa_admin():
        if region_editando["nombre"] is None:
            messagebox.showwarning("Envíos", "Selecciona primero una región de la tabla.", parent=ventana)
            return
        try:
            bd_envios.guardar_tarifa(region_editando["nombre"], entrada_costo_envio.get(), entrada_dias_envio.get())
        except ValueError as e:
            messagebox.showwarning("Envíos", str(e), parent=ventana)
            return
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo guardar la tarifa: {e}", parent=ventana)
            return
        refrescar_tarifas()
        messagebox.showinfo("Envíos", f"Tarifa de {region_editando['nombre']} actualizada.", parent=ventana)

    tk.Button(frame_envios, text="Guardar tarifa", command=guardar_tarifa_admin,
              bg="#0d6efd", fg="white", activebackground="#0d6efd", activeforeground="white",
              relief="flat", bd=0, font=("Segoe UI", 10), padx=14, pady=6).grid(row=6, column=0, sticky="w", pady=(10, 0))

    tk.Label(frame_envios, text="Envío gratis desde (CLP)", font=("Segoe UI", 10), anchor="w").grid(row=7, column=0, sticky="ew", pady=(18, 2))
    tk.Label(frame_envios, text="Región de la tienda", font=("Segoe UI", 10), anchor="w").grid(row=7, column=1, sticky="ew", pady=(18, 2), padx=(10, 0))
    entrada_monto_gratis = tk.Entry(frame_envios, width=12, relief="flat", highlightthickness=1,
                                    highlightbackground="#ced4da", highlightcolor="#0d6efd")
    entrada_monto_gratis.grid(row=8, column=0, sticky="ew", ipady=6)
    selector_region_tienda = ttk.Combobox(frame_envios, state="readonly", font=("Segoe UI", 10), values=bd_envios.REGIONES)
    selector_region_tienda.grid(row=8, column=1, sticky="ew", padx=(10, 0))

    def guardar_config_admin():
        try:
            bd_envios.guardar_config(entrada_monto_gratis.get(), selector_region_tienda.get())
        except ValueError as e:
            messagebox.showwarning("Envíos", str(e), parent=ventana)
            return
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}", parent=ventana)
            return
        messagebox.showinfo("Envíos", "Configuración de envío guardada.", parent=ventana)

    tk.Button(frame_envios, text="Guardar configuración", command=guardar_config_admin,
              bg="#6c757d", fg="white", activebackground="#6c757d", activeforeground="white",
              relief="flat", bd=0, font=("Segoe UI", 10), padx=14, pady=6).grid(row=9, column=0, sticky="w", pady=(10, 0))

    def abrir_envios():
        mostrar_seccion(frame_envios)
        refrescar_tarifas()


    # Frame de estadísticas por categoría
    Frame_estadisticas.grid_columnconfigure(0, weight=1)        # la columna se estira al ancho del panel

    # Mantenemos el titulo gris, como el del formulario
    tk.Label(Frame_estadisticas, text="Estadisticas", bg="#dcdde1", font=("Segoe UI", 12), pady=14).grid(row=0, column=0, sticky="ew", pady=(0,10))
    # Etiqueta encima del selector
    tk.Label(Frame_estadisticas, text="Categoria", font=("Segoe UI", 10), anchor="w").grid(row=1, column=0, sticky="ew", pady=(8, 2))

    categorias = sorted({producto[4] for producto in bd.mostrar_productos()})
    categoria_estadisticas = tk.StringVar()
    selector_categoria = ttk.Combobox(
        Frame_estadisticas,
        textvariable=categoria_estadisticas,
        values=categorias,
        state="readonly",
        font=("Segoe UI", 10),
        width=30,                       
    )
    selector_categoria.grid(row=2, column=0, sticky="ew", pady=4)
    if categorias:
        selector_categoria.current(0)

    # Botón principal (Calcular)
    boton_calcular = tk.Button(
        Frame_estadisticas, text="Calcular",
        command=lambda: F.mostrar_estadisticas(selector_categoria, resultado_estadisticas),
        bg="#0d6efd", fg="white", activebackground="#0d6efd", activeforeground="white",
        relief="flat", bd=0, font=("Segoe UI", 10), padx=14, pady=6,
    )
    boton_calcular.grid(row=3, column=0, sticky="w", pady=(16, 0))

    # Botón secundario (Total)
    boton_total = tk.Button(
        Frame_estadisticas, text="Calcular total del inventario",
        command=lambda: F.mostrar_total_inventario(resultado_estadisticas),
        bg="#6c757d", fg="white", activebackground="#6c757d", activeforeground="white",
        relief="flat", bd=0, font=("Segoe UI", 10), padx=14, pady=6,
    )
    boton_total.grid(row=4, column=0, sticky="w", pady=(8, 0))

    # Parte del resultado.
    # wraplength corta el texto en líneas de máximo 300 px.
    # Sin eso, un resultado largo ensancharía el panel y empujaría la tabla.
    resultado_estadisticas = tk.Label(Frame_estadisticas, justify="left", anchor="w",
                                      font=("Segoe UI", 10), wraplength=300)
    resultado_estadisticas.grid(row=5, column=0, sticky="ew", pady=(16, 0))

    # Seccion para Vaciar inventario:
    TODO = "-- Todo el inventario --"

    selector_vaciar = ttk.Combobox(Frame_botones, state="readonly", width=22)
    selector_vaciar.grid(row=1, column=9, padx=(0, 5), pady=10)

    def actualizar_selector_vaciar():
        # Vuelve a leer las categorías de la BD (así no queda una categoría ya vaciada)
        categorias_bd = sorted({p[4] for p in bd.mostrar_productos() if p[4] and p[4].strip()})
        selector_vaciar["values"] = [TODO] + categorias_bd
        selector_vaciar.current(0)

        # El selector de estadísticas también se actualiza
        selector_categoria["values"] = categorias_bd
        if categorias_bd:
            selector_categoria.current(0)
        else:
            selector_categoria.set("")
        resultado_estadisticas.config(text="")

    def vaciar():
        boton_vaciar.config(state="disabled")       # evita clics repetidos mientras se procesa
        try:
            seleccion = selector_vaciar.get()      

            if not bd.mostrar_productos():
                messagebox.showinfo("Inventario vacío", "No hay productos para vaciar.", parent=ventana)
                return

            if seleccion == TODO:
                texto = "¿seguro que quieres vaciar todo el inventario? Esta accion eliminara todos los productos."
            else:
                texto = f"¿seguro que quieres vaciar la categoria '{seleccion}'? Se eliminarán todos los productos de esa categoría."
            # Si el usuario presiona "No", askyesno devuelve False y se cancela todo.
            if not messagebox.askyesno("Confirmación", texto, parent=ventana):
                return
  
            if seleccion == TODO:
                bd.vaciar_inventario()
                aviso = "Se vació todo el inventario."
            else:
                bd.vaciar_categoria(seleccion)
                aviso = f"Se vació la categoría '{seleccion}'."

            F.inventario.productos = F.I().productos    # actualiza la lista en memoria
            F.mostrar_productos(Frame_producto)
            actualizar_selector_vaciar()
            messagebox.showinfo("Listo", aviso, parent=ventana)
        finally:
            boton_vaciar.config(state="normal")

    boton_vaciar = tk.Button(Frame_botones, text="Vaciar", command=vaciar)
    boton_vaciar.grid(row=1, column=10, padx=(0, 20), pady=10)

    # Botones provicionales, aun no sirven
    boton_carritos = tk.Button(Frame_botones, text="Carritos", command=lambda: abrir_carritos())
    boton_ventas = tk.Button(Frame_botones, text="Ventas", command=lambda: abrir_ventas())
    boton_carritos.grid(column=6, row=1)
    boton_ventas.grid(column=7, row=1)
    # cupones y envios van juntos en la columna 8 para no mover el resto de la barra
    frame_cupones_envios = tk.Frame(Frame_botones, bg="#f1f3f5")
    frame_cupones_envios.grid(column=8, row=1, sticky="w")
    boton_cupones = tk.Button(frame_cupones_envios, text="Cupones", command=lambda: mostrar_seccion(frame_cupones))
    boton_cupones.pack(side="left")
    boton_envios = tk.Button(frame_cupones_envios, text="Envíos", command=lambda: abrir_envios())
    boton_envios.pack(side="left")

    # Frame de carritos (solo lectura)
    frame_carritos.grid_columnconfigure(0, weight=1)        # la columna se estira al ancho del panel

    # Titulo gris, igual que el resto de secciones
    tk.Label(frame_carritos, text="Carritos", bg="#dcdde1", font=("Segoe UI", 12), pady=14).grid(row=0, column=0, sticky="ew", pady=(0, 10))
    tk.Label(frame_carritos, text="Carrito de usuario", font=("Segoe UI", 10), anchor="w").grid(row=1, column=0, sticky="ew", pady=(8, 2))

    selector_carrito = ttk.Combobox(frame_carritos, state="readonly", font=("Segoe UI", 10), width=30)
    selector_carrito.grid(row=2, column=0, sticky="ew", pady=4)

    boton_actualizar_carritos = tk.Button(
        frame_carritos, text="Actualizar", command=lambda: refrescar_carritos(),
        bg="#0d6efd", fg="white", activebackground="#0d6efd", activeforeground="white",
        relief="flat", bd=0, font=("Segoe UI", 10), padx=14, pady=6,
    )
    boton_actualizar_carritos.grid(row=3, column=0, sticky="w", pady=(16, 0))

    # Resumen del carrito seleccionado (unidades y total)
    resumen_carrito = tk.Label(frame_carritos, justify="left", anchor="w", font=("Segoe UI", 10), wraplength=300)
    resumen_carrito.grid(row=4, column=0, sticky="ew", pady=(16, 8))

    # Tabla con el mismo estilo que la de productos (el estilo "Productos.Treeview" lo crea FuncionBotones)
    tabla_carrito = ttk.Treeview(frame_carritos, columns=("producto", "cantidad", "precio", "subtotal"),
                                 show="headings", style="Productos.Treeview", height=6)
    for col, (texto, ancho, ancla) in {
        "producto": ("PRODUCTO", 140, "w"),
        "cantidad": ("CANT.", 50, "center"),
        "precio":   ("PRECIO", 90, "e"),
        "subtotal": ("SUBTOTAL", 100, "e"),
    }.items():
        tabla_carrito.heading(col, text=texto)
        tabla_carrito.column(col, width=ancho, anchor=ancla)
    tabla_carrito.tag_configure("par", background="#ffffff")
    tabla_carrito.tag_configure("impar", background="#e0e0e0")
    tabla_carrito.grid(row=5, column=0, sticky="ew")

    ids_carritos = []       # ids de los carritos en el mismo orden que el selector

    def mostrar_items_carrito(event=None):
        tabla_carrito.delete(*tabla_carrito.get_children())
        posicion = selector_carrito.current()
        if posicion < 0:
            resumen_carrito.config(text="No hay carritos todavía.")
            return
        try:
            items = bd_carrito.items_de_carrito(ids_carritos[posicion])
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo leer el carrito: {e}", parent=ventana)
            return
        unidades = sum(item[2] for item in items)
        total = sum(item[4] for item in items)
        resumen_carrito.config(text=f"Unidades: {unidades}\nTotal: ${total:,.0f}")
        for i, (_id_producto, nombre_p, cantidad, precio, subtotal) in enumerate(items):
            tabla_carrito.insert("", "end",
                                 values=(nombre_p, cantidad, f"${precio:,.0f}", f"${subtotal:,.0f}"),
                                 tags=("par" if i % 2 == 0 else "impar",))

    def refrescar_carritos():
        # intentamos conservar el carrito que se estaba viendo
        posicion = selector_carrito.current()
        previo = ids_carritos[posicion] if 0 <= posicion < len(ids_carritos) else None
        try:
            carritos = bd_carrito.listar_carritos()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudieron leer los carritos: {e}", parent=ventana)
            return
        ids_carritos.clear()
        etiquetas = []
        for id_c, usuario_c, _fecha, estado, unidades, _total in carritos:
            ids_carritos.append(id_c)
            etiquetas.append(f"#{id_c} · {usuario_c} · {estado}")
        selector_carrito["values"] = etiquetas
        if ids_carritos:
            selector_carrito.current(ids_carritos.index(previo) if previo in ids_carritos else 0)
        else:
            selector_carrito.set("")
        mostrar_items_carrito()

    def abrir_carritos():
        mostrar_seccion(frame_carritos)
        refrescar_carritos()

    selector_carrito.bind("<<ComboboxSelected>>", mostrar_items_carrito)

    frame_ventas.grid_columnconfigure(0, weight=1)

    tk.Label(frame_ventas, text="Ventas", bg="#dcdde1", font=("Segoe UI", 12), pady=14).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
    tk.Label(frame_ventas, text="Haz click en un comprobante para ver sus productos", font=("Segoe UI", 10),
             anchor="w", justify="left", wraplength=340).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))

    tabla_ventas = ttk.Treeview(frame_ventas, columns=("id", "cliente", "fecha"),
                                show="headings", style="Productos.Treeview", height=9)
    for col, (texto, ancho, ancla) in {
        "id":      ("N°", 50, "center"),
        "cliente": ("CLIENTE", 130, "w"),
        "fecha":   ("FECHA", 140, "center"),
    }.items():
        tabla_ventas.heading(col, text=texto)
        tabla_ventas.column(col, width=ancho, anchor=ancla)
    tabla_ventas.tag_configure("par", background="#ffffff")
    tabla_ventas.tag_configure("impar", background="#e0e0e0")
    tabla_ventas.grid(row=2, column=0, sticky="ew")

    scroll_ventas = ttk.Scrollbar(frame_ventas, orient="vertical", command=tabla_ventas.yview)
    tabla_ventas.configure(yscrollcommand=scroll_ventas.set)
    scroll_ventas.grid(row=2, column=1, sticky="ns")

    boton_actualizar_ventas = tk.Button(
        frame_ventas, text="Actualizar", command=lambda: refrescar_ventas(),
        bg="#0d6efd", fg="white", activebackground="#0d6efd", activeforeground="white",
        relief="flat", bd=0, font=("Segoe UI", 10), padx=14, pady=6,
    )
    boton_actualizar_ventas.grid(row=3, column=0, sticky="w", pady=(16, 0))

    aviso_ventas = tk.Label(frame_ventas, anchor="w", font=("Segoe UI", 10))
    aviso_ventas.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    datos_ventas = {}

    def formatear_fecha(fecha_iso):
        try:
            return datetime.fromisoformat(fecha_iso).strftime("%d-%m-%Y %H:%M")
        except (ValueError, TypeError):
            return str(fecha_iso)

    def refrescar_ventas():
        try:
            ventas = bd_ventas.listar_ventas()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudieron leer las ventas: {e}", parent=ventana)
            return
        tabla_ventas.delete(*tabla_ventas.get_children())
        datos_ventas.clear()
        for i, (id_v, fecha_v, cliente_v, total_v) in enumerate(ventas):
            datos_ventas[id_v] = (fecha_v, cliente_v, total_v)
            tabla_ventas.insert("", "end", iid=str(id_v),
                                values=(id_v, cliente_v, formatear_fecha(fecha_v)),
                                tags=("par" if i % 2 == 0 else "impar",))
        aviso_ventas.config(text="" if ventas else "Todavía no hay ventas.")

    def abrir_detalle_venta(id_venta):
        if id_venta not in datos_ventas:
            return
        fecha_v, cliente_v, total_v = datos_ventas[id_venta]
        try:
            items = bd_ventas.items_de_venta(id_venta)
            stock_actual = {p[0]: p[3] for p in bd.mostrar_productos()}
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo leer el detalle de la venta: {e}", parent=ventana)
            return

        detalle = tk.Toplevel(ventana)
        detalle.title(f"Comprobante N°{id_venta}")
        detalle.geometry("780x470")
        detalle.transient(ventana)

        tk.Label(detalle, text=f"Comprobante N°{id_venta}", bg="#dcdde1",
                 font=("Segoe UI", 12), pady=14).pack(fill="x")
        tk.Label(detalle, text=f"Cliente: {cliente_v}\nFecha: {formatear_fecha(fecha_v)}",
                 font=("Segoe UI", 10), justify="left", anchor="w").pack(fill="x", padx=20, pady=(12, 8))

        marco_tabla = tk.Frame(detalle)
        marco_tabla.pack(fill="both", expand=True, padx=20)

        tabla_detalle = ttk.Treeview(marco_tabla, columns=("id", "producto", "cantidad", "precio", "stock", "subtotal"),
                                     show="headings", style="Productos.Treeview", height=5)
        for col, (texto, ancho, ancla) in {
            "id":       ("ID", 50, "center"),
            "producto": ("PRODUCTO", 220, "w"),
            "cantidad": ("CANT.", 75, "center"),
            "precio":   ("PRECIO", 105, "e"),
            "stock":    ("STOCK ACTUAL", 140, "center"),
            "subtotal": ("SUBTOTAL", 115, "e"),
        }.items():
            tabla_detalle.heading(col, text=texto)
            tabla_detalle.column(col, width=ancho, anchor=ancla)
        tabla_detalle.tag_configure("par", background="#ffffff")
        tabla_detalle.tag_configure("impar", background="#e0e0e0")
        tabla_detalle.tag_configure("sin_stock", foreground="#e8283c")

        scroll_detalle = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla_detalle.yview)
        tabla_detalle.configure(yscrollcommand=scroll_detalle.set)
        scroll_detalle.pack(side="right", fill="y")
        tabla_detalle.pack(side="left", fill="both", expand=True)

        for i, (id_producto, nombre_p, cantidad, precio, subtotal_item) in enumerate(items):
            stock = stock_actual.get(id_producto)
            etiquetas = ["par" if i % 2 == 0 else "impar"]
            if stock == 0:
                etiquetas.append("sin_stock")
            tabla_detalle.insert("", "end",
                                 values=(id_producto, nombre_p, cantidad, f"${precio:,.0f}",
                                         "Eliminado" if stock is None else stock, f"${subtotal_item:,.0f}"),
                                 tags=tuple(etiquetas))

        if items:
            subtotal = sum(item[4] for item in items)
            # La venta guarda el total ya con descuento: de ahí se deduce el neto y el descuento del cupón
            neto = round(total_v / 1.19)
            descuento = subtotal - neto
            iva = total_v - neto
            resumen = f"Subtotal: ${subtotal:,.0f}\n"
            if descuento > 1:       # tolerancia de 1 peso por redondeo
                resumen += f"Descuento cupón: -${descuento:,.0f}\nSubtotal neto: ${neto:,.0f}\n"
            resumen += f"IVA (19%): ${iva:,.0f}"
        else:
            resumen = "Esta venta no tiene el detalle de productos guardado."
        tk.Label(detalle, text=resumen, font=("Segoe UI", 10), justify="right", anchor="e").pack(fill="x", padx=20, pady=(10, 0))
        tk.Label(detalle, text=f"Total de la compra: ${total_v:,.0f}", font=("Segoe UI", 11, "bold"),
                 anchor="e").pack(fill="x", padx=20, pady=(2, 14))

    def al_click_venta(event):
        if tabla_ventas.identify_region(event.x, event.y) != "cell":
            return
        fila = tabla_ventas.identify_row(event.y)
        if not fila:
            return
        abrir_detalle_venta(int(fila))

    tabla_ventas.bind("<Button-1>", al_click_venta)

    def abrir_ventas():
        mostrar_seccion(frame_ventas)
        refrescar_ventas()

        # ---------- estilo de la barra superior ----------

    botones_barra = (boton_ingreso, boton_estadisticas, boton_admin, boton_vaciar, boton_carritos, boton_ventas, boton_cupones, boton_envios)

    # El for repite lo mismo con cada botón.
    for b in botones_barra:
        b.config(       
            bg="#f1f3f5",                 # mismo color que la barra, así parece "sin caja"
            fg="#212529",                 # letra casi negra
            activebackground="#dee2e6",   # color mientras lo estás presionando
            activeforeground="#212529",
            relief="flat",                # sin relieve de botón clásico
            bd=0,                         # sin borde
            font=("Segoe UI", 10),
            padx=15, pady=6,              # espacio interno
        )

    # El botón vaciar lo dejamos distinto.
    boton_vaciar.config(bg="#fd0d0d", fg="white",
                        activebackground="#c9202f", activeforeground="white")
    actualizar_selector_vaciar()
    mostrar_seccion(Frame_ingreso)      # mostramos el formulario apensa se abre la ventana
    #frame de los productos
    F.mostrar_productos(Frame_producto)